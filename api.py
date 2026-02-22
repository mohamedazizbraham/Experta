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

from database import CATALOGUE_COMPLET
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


class RecommendationResponse(BaseModel):
    id: str
    user_id: str
    source: str
    input: Dict[str, Any]
    decision: Dict[str, Any]
    created_at: datetime


class BestDecisionComplementTakenRequest(BaseModel):
    taken_at: Optional[datetime] = None


class RecommendationIntakeItemRequest(BaseModel):
    supplement_id: Optional[str] = Field(default=None, max_length=200)
    supplement_name: str = Field(min_length=1, max_length=200)
    objective_key: Optional[str] = Field(default=None, max_length=200)
    objective_label: Optional[str] = Field(default=None, max_length=200)
    taken: bool = True
    taken_at: Optional[datetime] = None


class RecommendationIntakesBulkRequest(BaseModel):
    intakes: List[RecommendationIntakeItemRequest] = Field(default_factory=list)


class RecommendationIntakeResponse(BaseModel):
    id: str
    user_id: str
    recommendation_id: str
    supplement_id: Optional[str] = None
    supplement_name: str
    objective_key: Optional[str] = None
    objective_label: Optional[str] = None
    taken: bool
    taken_at: datetime
    created_at: datetime


class RecommendationIntakesBulkResponse(BaseModel):
    recommendation_id: str
    saved_count: int
    intakes: List[RecommendationIntakeResponse]
    decision: Dict[str, Any]


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


def _build_complement_product_names() -> set[str]:
    names: set[str] = set()
    sheets = CATALOGUE_COMPLET.get("complement_alimentaire") or []
    for sheet in sheets:
        if not isinstance(sheet, dict):
            continue
        raw_name = sheet.get("name")
        if not isinstance(raw_name, str):
            continue
        name = raw_name.strip()
        if name:
            names.add(name.casefold())
    return names


COMPLEMENT_PRODUCT_NAMES = _build_complement_product_names()


def _is_complement_alimentaire_product(product_name: Any) -> bool:
    if not isinstance(product_name, str):
        return False
    return product_name.strip().casefold() in COMPLEMENT_PRODUCT_NAMES


def _to_utc_datetime(value: Optional[datetime]) -> datetime:
    if value is None:
        return _now_utc()
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _recommendation_item_product_name(item: Dict[str, Any]) -> Optional[str]:
    if not isinstance(item, dict):
        return None

    candidates = [
        item.get("produit"),
        item.get("product"),
        item.get("nom"),
        item.get("name"),
        item.get("supplement"),
        item.get("intervention"),
    ]
    for value in candidates:
        if isinstance(value, str):
            txt = value.strip()
            if txt:
                return txt
    return None


def _with_best_decision_complement_times(decision_payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(decision_payload, dict):
        return {}

    decision = dict(decision_payload)
    recommendations = decision.get("recommendations")
    if isinstance(recommendations, list):
        recommendations_copy: List[Any] = []
        for item in recommendations:
            if not isinstance(item, dict):
                recommendations_copy.append(item)
                continue
            item_copy = dict(item)
            if not isinstance(item_copy.get("complement_taken_times"), list):
                item_copy["complement_taken_times"] = []
            recommendations_copy.append(item_copy)
        decision["recommendations"] = recommendations_copy

    best_decision = decision.get("best_decision")
    if not isinstance(best_decision, dict):
        return decision

    best_decision_copy = dict(best_decision)
    if _is_complement_alimentaire_product(best_decision_copy.get("produit")):
        if not isinstance(best_decision_copy.get("complement_taken_times"), list):
            best_decision_copy["complement_taken_times"] = []

    decision["best_decision"] = best_decision_copy
    return decision


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
def recommendation_public(doc: Dict[str, Any]) -> Dict[str, Any]:
    decision = _with_best_decision_complement_times(doc.get("decision", {}))
    return {
        "id": str(doc["_id"]),
        "user_id": str(doc["user_id"]),
        "source": doc.get("source", "profile"),
        "input": doc.get("input", {}),
        "decision": decision,
        "created_at": doc.get("created_at"),
    }


def _clean_optional_text(value: Optional[str]) -> Optional[str]:
    if not isinstance(value, str):
        return None
    txt = value.strip()
    return txt if txt else None


def recommendation_intake_public(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(doc["_id"]),
        "user_id": str(doc["user_id"]),
        "recommendation_id": str(doc["recommendation_id"]),
        "supplement_id": doc.get("supplement_id"),
        "supplement_name": doc.get("supplement_name", ""),
        "objective_key": doc.get("objective_key"),
        "objective_label": doc.get("objective_label"),
        "taken": bool(doc.get("taken", False)),
        "taken_at": doc.get("taken_at"),
        "created_at": doc.get("created_at"),
    }


async def save_recommendation(
    db: AsyncIOMotorDatabase,
    *,
    user_id: ObjectId,
    source: str,
    input_payload: Dict[str, Any],
    decision_payload: Dict[str, Any],
) -> Dict[str, Any]:
    now = _now_utc()
    decision_payload = _with_best_decision_complement_times(decision_payload)
    doc = {
        "user_id": user_id,
        "source": source,
        "input": input_payload,
        "decision": decision_payload,
        "created_at": now,
    }
    result = await db.recommendations.insert_one(doc)
    created = await db.recommendations.find_one({"_id": result.inserted_id})
    if not created:
        raise HTTPException(status_code=500, detail="Failed to save recommendation")
    return created


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
async def decide_for_me(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user),
):
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
    decision = _with_best_decision_complement_times(decision)
    saved = await save_recommendation(
        db,
        user_id=user["_id"],
        source="profile",
        input_payload=prepared,
        decision_payload=decision,
    )
    return {
        "user_id": str(user["_id"]),
        "derived_input": prepared,
        "decision": decision,
        "saved_recommendation_id": str(saved["_id"]),
        "saved_at": saved["created_at"],
    }


@app.get("/users/me/recommendations", response_model=List[RecommendationResponse])
async def list_my_recommendations(
    limit: int = 20,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user),
):
    limit = max(1, min(limit, 100))
    cursor = (
        db.recommendations
        .find({"user_id": user["_id"]})
        .sort("created_at", -1)
        .limit(limit)
    )
    items = await cursor.to_list(length=limit)
    return [recommendation_public(item) for item in items]


@app.get("/users/me/recommendations/{recommendation_id}", response_model=RecommendationResponse)
async def get_my_recommendation(
    recommendation_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user),
):
    try:
        rec_id = ObjectId(recommendation_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid recommendation id")

    item = await db.recommendations.find_one({"_id": rec_id, "user_id": user["_id"]})
    if not item:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return recommendation_public(item)


@app.get(
    "/users/me/recommendations/{recommendation_id}/intakes",
    response_model=List[RecommendationIntakeResponse],
)
async def list_my_recommendation_intakes(
    recommendation_id: str,
    limit: int = 200,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user),
):
    limit = max(1, min(limit, 500))

    try:
        rec_id = ObjectId(recommendation_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid recommendation id")

    recommendation = await db.recommendations.find_one({"_id": rec_id, "user_id": user["_id"]})
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    cursor = (
        db.recommendation_intakes
        .find({"recommendation_id": rec_id, "user_id": user["_id"]})
        .sort("taken_at", -1)
        .limit(limit)
    )
    docs = await cursor.to_list(length=limit)
    return [recommendation_intake_public(doc) for doc in docs]


@app.post(
    "/users/me/recommendations/{recommendation_id}/intakes/bulk",
    response_model=RecommendationIntakesBulkResponse,
)
async def save_my_recommendation_intakes(
    recommendation_id: str,
    payload: RecommendationIntakesBulkRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user),
):
    if not payload.intakes:
        raise HTTPException(status_code=400, detail="No intakes provided")

    try:
        rec_id = ObjectId(recommendation_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid recommendation id")

    recommendation = await db.recommendations.find_one({"_id": rec_id, "user_id": user["_id"]})
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    decision = _with_best_decision_complement_times(
        recommendation.get("decision", {}) if isinstance(recommendation, dict) else {}
    )
    best_decision = decision.get("best_decision") if isinstance(decision, dict) else None
    recommendations = decision.get("recommendations") if isinstance(decision, dict) else None

    best_product_name: Optional[str] = None
    if isinstance(best_decision, dict):
        best_product_name = _clean_optional_text(_recommendation_item_product_name(best_decision))
        if best_product_name and not _is_complement_alimentaire_product(best_product_name):
            best_product_name = None

    now = _now_utc()
    docs: List[Dict[str, Any]] = []

    for i, intake in enumerate(payload.intakes):
        supplement_name = _clean_optional_text(intake.supplement_name)
        if not supplement_name:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid supplement_name at intakes[{i}]",
            )

        taken_at = _to_utc_datetime(intake.taken_at)
        intake_doc = {
            "user_id": user["_id"],
            "recommendation_id": rec_id,
            "supplement_id": _clean_optional_text(intake.supplement_id),
            "supplement_name": supplement_name,
            "objective_key": _clean_optional_text(intake.objective_key),
            "objective_label": _clean_optional_text(intake.objective_label),
            "taken": bool(intake.taken),
            "taken_at": taken_at,
            "created_at": now,
        }
        docs.append(intake_doc)

        if (
            best_product_name
            and intake_doc["taken"] is True
            and supplement_name.casefold() == best_product_name.casefold()
        ):
            best_times = best_decision.get("complement_taken_times") if isinstance(best_decision, dict) else None
            if isinstance(best_times, list):
                best_times.append(taken_at)

        if intake_doc["taken"] is True and isinstance(recommendations, list):
            supplement_key = supplement_name.casefold()
            for rec_item in recommendations:
                if not isinstance(rec_item, dict):
                    continue
                rec_name = _recommendation_item_product_name(rec_item)
                if not rec_name or rec_name.casefold() != supplement_key:
                    continue
                rec_times = rec_item.get("complement_taken_times")
                if isinstance(rec_times, list):
                    rec_times.append(taken_at)

    result = await db.recommendation_intakes.insert_many(docs)
    created_docs = await (
        db.recommendation_intakes
        .find({"_id": {"$in": result.inserted_ids}})
        .sort("created_at", -1)
        .to_list(length=len(result.inserted_ids))
    )

    await db.recommendations.update_one(
        {"_id": rec_id, "user_id": user["_id"]},
        {"$set": {"decision": decision}},
    )

    updated_recommendation = await db.recommendations.find_one({"_id": rec_id, "user_id": user["_id"]})
    if not updated_recommendation:
        raise HTTPException(status_code=500, detail="Failed to update recommendation")

    return {
        "recommendation_id": recommendation_id,
        "saved_count": len(created_docs),
        "intakes": [recommendation_intake_public(doc) for doc in created_docs],
        "decision": _with_best_decision_complement_times(updated_recommendation.get("decision", {})),
    }


@app.post(
    "/users/me/recommendations/{recommendation_id}/best-decision/complement-times",
    response_model=RecommendationResponse,
)
async def add_best_decision_complement_time(
    recommendation_id: str,
    payload: Optional[BestDecisionComplementTakenRequest] = None,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user),
):
    try:
        rec_id = ObjectId(recommendation_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid recommendation id")

    item = await db.recommendations.find_one({"_id": rec_id, "user_id": user["_id"]})
    if not item:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    decision = _with_best_decision_complement_times(
        item.get("decision", {}) if isinstance(item, dict) else {}
    )
    best_decision = decision.get("best_decision") if isinstance(decision, dict) else None
    if not isinstance(best_decision, dict):
        raise HTTPException(status_code=400, detail="This recommendation has no best decision")

    product_name = _recommendation_item_product_name(best_decision)
    if not _is_complement_alimentaire_product(product_name):
        raise HTTPException(
            status_code=400,
            detail="Best decision is not a complement_alimentaire product",
        )

    taken_at = _to_utc_datetime(payload.taken_at if payload else None)
    best_times = best_decision.get("complement_taken_times")
    if isinstance(best_times, list):
        best_times.append(taken_at)

    recommendations = decision.get("recommendations") if isinstance(decision, dict) else None
    if isinstance(recommendations, list):
        product_key = product_name.casefold() if isinstance(product_name, str) else None
        if product_key:
            for rec_item in recommendations:
                if not isinstance(rec_item, dict):
                    continue
                rec_name = _recommendation_item_product_name(rec_item)
                if not rec_name or rec_name.casefold() != product_key:
                    continue
                rec_times = rec_item.get("complement_taken_times")
                if isinstance(rec_times, list):
                    rec_times.append(taken_at)

    await db.recommendations.update_one(
        {"_id": rec_id, "user_id": user["_id"]},
        {"$set": {"decision": decision}},
    )

    updated = await db.recommendations.find_one({"_id": rec_id, "user_id": user["_id"]})
    if not updated:
        raise HTTPException(status_code=500, detail="Failed to update recommendation")
    return recommendation_public(updated)
