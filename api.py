from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastapi import Depends, FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field

from mongo import close_client, get_db
from security import create_access_token, decode_access_token, hash_password, verify_password
from service import decide as decide_rules

app = FastAPI(title="Experta + Backend API", version="2.0.0")
bearer = HTTPBearer(auto_error=False)


def _oid(x: Any) -> str:
    return str(x)


async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = creds.credentials
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    db = get_db()
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@app.on_event("startup")
async def _startup():
    db = get_db()
    await db.users.create_index("email", unique=True)


@app.on_event("shutdown")
async def _shutdown():
    await close_client()


@app.get("/health")
def health():
    return {"status": "ok"}


# -------------------------
# AUTH
# -------------------------

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@app.post("/auth/signup", response_model=TokenResponse)
async def signup(req: SignupRequest):
    db = get_db()
    existing = await db.users.find_one({"email": str(req.email).lower()})
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")

    doc = {
        "email": str(req.email).lower(),
        "password_hash": hash_password(req.password),
        "profile": {
            "personal": {}  # <- perso ici (name/age/sex) dans un sous-objet
        },
    }

    res = await db.users.insert_one(doc)
    token = create_access_token(str(res.inserted_id))
    return {"access_token": token}


@app.post("/auth/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    db = get_db()
    user = await db.users.find_one({"email": str(req.email).lower()})
    if not user or not verify_password(req.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(str(user["_id"]))
    return {"access_token": token}


# -------------------------
# USER / PROFILE
# -------------------------

class PersonalInfo(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=0, le=120)
    sex: Optional[str] = Field(default=None, description="male/female/other")
    birth_date: Optional[date] = None  # stocké en string ISO pour éviter bson.date


class ProfileUpdate(BaseModel):
    personal: Optional[PersonalInfo] = None

    activity_level: Optional[str] = Field(
        default=None,
        description="ex: sedentary, light, moderate, active, athlete",
    )

    # médical (utilisé ensuite pour filtrer / contra-indications)
    conditions: Optional[List[str]] = None
    diseases: Optional[List[str]] = None
    medications: Optional[List[str]] = None

    pregnancy: Optional[bool] = None
    breastfeeding: Optional[bool] = None

    goals: Optional[List[str]] = None


@app.get("/users/me")
async def me(include_personal: bool = True, user: dict = Depends(get_current_user)):
    # si tu veux “cacher” le perso, tu mets include_personal=false
    db = get_db()
    projection = {"password_hash": 0}
    if not include_personal:
        projection["profile.personal"] = 0

    fresh = await db.users.find_one({"_id": user["_id"]}, projection)
    if not fresh:
        raise HTTPException(404, "User not found")

    fresh["id"] = _oid(fresh["_id"])
    fresh.pop("_id", None)
    return fresh


@app.put("/users/me/profile")
async def update_profile(req: ProfileUpdate, user: dict = Depends(get_current_user)):
    db = get_db()
    payload = req.model_dump(exclude_unset=True)

    if "personal" in payload and payload["personal"] is not None:
        personal = payload["personal"]
        # birth_date (date) -> string ISO pour Mongo (évite InvalidDocument)
        if "birth_date" in personal and personal["birth_date"] is not None:
            personal["birth_date"] = personal["birth_date"].isoformat()
        payload["personal"] = personal

    set_fields = {f"profile.{k}": v for k, v in payload.items()}

    if not set_fields:
        return {"status": "no_changes"}

    await db.users.update_one({"_id": user["_id"]}, {"$set": set_fields})
    return {"status": "updated"}


# -------------------------
# DECIDE (RULE ENGINE)
# -------------------------

class DecideRequest(BaseModel):
    symptomes: List[str]
    conditions_medicales: List[str] = Field(default_factory=list)


@app.post("/decide")
async def decide_endpoint(req: DecideRequest):
    # moteur Experta = sync -> threadpool pour ne pas bloquer FastAPI
    return await run_in_threadpool(decide_rules, req.symptomes, req.conditions_medicales)
