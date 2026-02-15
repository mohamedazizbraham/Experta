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


def _clean_text_list(values: Any) -> List[str]:
    if not isinstance(values, list):
        return []

    out: List[str] = []
    for value in values:
        if isinstance(value, str):
            txt = value.strip()
            if txt:
                out.append(txt)
    return out


def _dedupe_keep_order(values: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for value in values:
        key = value.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out


def _decision_input_from_profile(profile: Dict[str, Any]) -> Dict[str, List[str]]:
    profile = profile or {}
    medical = profile.get("medical") or {}
    personal = profile.get("personal") or {}

    symptomes = _dedupe_keep_order(
        _clean_text_list(profile.get("goals"))
        + _clean_text_list(profile.get("symptomes"))
        + _clean_text_list(profile.get("symptoms"))
        + _clean_text_list(personal.get("symptomes"))
        + _clean_text_list(personal.get("symptoms"))
    )

    conditions_medicales = _dedupe_keep_order(
        _clean_text_list(medical.get("conditions"))
        + _clean_text_list(medical.get("diseases"))
        + _clean_text_list(medical.get("medications"))
        + _clean_text_list(medical.get("allergies"))
    )

    if medical.get("is_pregnant") is True:
        conditions_medicales.append("grossesse")
    if medical.get("is_breastfeeding") is True:
        conditions_medicales.append("allaitement")
    conditions_medicales = _dedupe_keep_order(conditions_medicales)

    return {
        "symptomes": symptomes,
        "conditions_medicales": conditions_medicales,
    }


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


@app.get("/decide/me")
async def decide_for_me(user: Dict[str, Any] = Depends(get_current_user)):
    profile = user.get("profile") or {}
    prepared = _decision_input_from_profile(profile)

    if not prepared["symptomes"]:
        raise HTTPException(
            status_code=400,
            detail=(
                "No usable symptoms/goals found in your profile. "
                "Update `profile.goals` or `profile.personal.symptomes` first."
            ),
        )

    decision = await run_in_threadpool(
        decide_rules,
        prepared["symptomes"],
        prepared["conditions_medicales"],
    )
    return {
        "user_id": str(user["_id"]),
        "derived_input": prepared,
        "decision": decision,
    }
