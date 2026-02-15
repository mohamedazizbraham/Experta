<<<<<<< HEAD
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
=======
# api.py
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from bson import ObjectId
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, EmailStr, Field
from starlette.concurrency import run_in_threadpool

from mongo import get_db
from security import create_access_token, decode_access_token, hash_password, verify_password
from service import decide as decide_rules

app = FastAPI(title="AJA Backend", version="1.0.0")

# ✅ CORS (important for Expo Web)
origins = [
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    "http://localhost:19006",
    "http://127.0.0.1:19006",
    # Optionnel:
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # en dev tu peux mettre ["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: str
    profile: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PersonalInfoUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)

    sex: Optional[Literal["male", "female", "other"]] = None
    weight_kg: Optional[float] = Field(None, ge=0, le=500)
    height_cm: Optional[int] = Field(None, ge=0, le=300)

    age_range: Optional[
        Literal[
            "-18",
            "18-30",
            "31-45",
            "46-60",
            "+60",
        ]
    ] = None


class MedicalInfoUpdate(BaseModel):
    is_pregnant: Optional[bool] = None
    is_breastfeeding: Optional[bool] = None
    conditions: Optional[List[str]] = None
    diseases: Optional[List[str]] = None
    medications: Optional[List[str]] = None
    allergies: Optional[List[str]] = None


class ProfileUpdate(BaseModel):
    personal: Optional[PersonalInfoUpdate] = None
    activity_level: Optional[Literal["sedentary", "light", "moderate", "active", "very_active"]] = None
    goals: Optional[List[str]] = None
    medical: Optional[MedicalInfoUpdate] = None


class DecideRequest(BaseModel):
    symptomes: List[str]
    conditions_medicales: Optional[List[str]] = None


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _to_mongo_value(v: Any) -> Any:
    if isinstance(v, date) and not isinstance(v, datetime):
        return v.isoformat()
    return v


def _flatten(prefix: str, obj: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in obj.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(_flatten(key, v))
        else:
            out[key] = _to_mongo_value(v)
    return out


def user_public(u: Dict[str, Any], include_personal: bool = True) -> Dict[str, Any]:
    profile = u.get("profile") or {}
    if not include_personal and isinstance(profile, dict):
        profile = {k: v for k, v in profile.items() if k != "personal"}

    return {
        "id": str(u["_id"]),
        "email": u["email"],
        "role": u.get("role", "user"),
        "profile": profile,
        "created_at": u.get("created_at"),
        "updated_at": u.get("updated_at"),
    }


# ✅✅✅ FIX PRINCIPAL: payload JWT -> user_id = payload["sub"]
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> Dict[str, Any]:
    try:
        payload = decode_access_token(token)   # dict
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication")

        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication")


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/auth/signup", response_model=TokenResponse)
async def signup(req: SignupRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    existing = await db.users.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    now = _now_utc()
    user_doc = {
        "email": req.email,
        "password_hash": hash_password(req.password),
        "role": "user",
        "profile": {
            "personal": {},
            "medical": {},
            "activity_level": None,
            "goals": [],
        },
        "created_at": now,
        "updated_at": now,
    }

    result = await db.users.insert_one(user_doc)
    token = create_access_token(str(result.inserted_id))
    created = await db.users.find_one({"_id": result.inserted_id})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_public(created, include_personal=True),
    }


@app.post("/auth/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    user = await db.users.find_one({"email": req.email})
    if not user or not verify_password(req.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(str(user["_id"]))
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_public(user, include_personal=True),
    }


@app.get("/users/me", response_model=UserResponse)
async def me(
    include_personal: bool = True,
    user: Dict[str, Any] = Depends(get_current_user),
):
    return user_public(user, include_personal=include_personal)


@app.put("/users/me/profile", response_model=UserResponse)
async def update_profile(
    payload: ProfileUpdate,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user),
):
    data = payload.model_dump(exclude_none=True)
    if not data:
        return user_public(user)

    # Compat: si first_name/last_name envoyés, construire name
    if isinstance(data.get("personal"), dict):
        personal = data["personal"]
        if "name" not in personal and ("first_name" in personal or "last_name" in personal):
            old_personal = ((user.get("profile") or {}).get("personal") or {})
            first = (personal.get("first_name") or old_personal.get("first_name") or "").strip()
            last = (personal.get("last_name") or old_personal.get("last_name") or "").strip()
            full = (" ".join([x for x in [first, last] if x])).strip()
            if full:
                personal["name"] = full

    set_fields = _flatten("profile", data)
    set_fields["updated_at"] = _now_utc()

    await db.users.update_one({"_id": user["_id"]}, {"$set": set_fields})
    user2 = await db.users.find_one({"_id": user["_id"]})
    return user_public(user2)


@app.post("/decide")
async def decide(req: DecideRequest):
    return await run_in_threadpool(decide_rules, req.symptomes, req.conditions_medicales)
>>>>>>> origin/master
