# api.py
from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
import random
import re
from typing import Any, Dict, List, Literal, Optional, Tuple
import unicodedata
from zoneinfo import ZoneInfo

from bson import ObjectId
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, EmailStr, Field
from starlette.concurrency import run_in_threadpool

from database import CATALOGUE_COMPLET
from goals import (
    canonical_goals_for_symptom,
    canonicalize_goal,
    canonicalize_goal_list,
    goal_options,
    symptoms_for_goals,
)
from mongo import get_db
from security import create_access_token, decode_access_token, hash_password, verify_password
from service import decide as decide_rules

app = FastAPI(title="AJA Backend", version="1.0.0")

APP_TIME_ZONE = ZoneInfo("Europe/Paris")

# ✅ CORS (important for Expo Web)
origins = [
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    "http://localhost:8082",
    "http://127.0.0.1:8082",
    "http://localhost:8083",
    "http://127.0.0.1:8083",
    "http://localhost:19006",
    "http://127.0.0.1:19006",
    # Optionnel:
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # en dev tu peux mettre ["*"]
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
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


class EmailAvailabilityResponse(BaseModel):
    available: bool
    normalized_email: str
    reason: Optional[str] = None
    suggestion: Optional[str] = None


class PersonalInfoUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    birth_date: Optional[date] = None

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
    supplement_id: Any = None
    supplement_name: Any = None
    objective_key: Any = None
    objective_label: Any = None
    taken: Any = True
    taken_at: Any = None


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


class GoalOptionResponse(BaseModel):
    id: str
    label: str


class EncyclopedieSupplementSummaryResponse(BaseModel):
    id: str
    name: str
    category: str
    description: str
    molecules: List[str] = Field(default_factory=list)


class EncyclopedieSupplementDetailResponse(EncyclopedieSupplementSummaryResponse):
    benefits: List[str] = Field(default_factory=list)
    dosage: Optional[str] = None
    sources: List[str] = Field(default_factory=list)


class WeeklyProgressItem(BaseModel):
    day: str
    completed: bool


class WeeklyCompletionPoint(BaseModel):
    day: str
    ymd: str
    percent: int


class EvolutionPoint(BaseModel):
    day: int
    value: int


class MonthlyHeatmapCell(BaseModel):
    day: int
    intensity: int


class DailyIntakeItem(BaseModel):
    time: str
    name: str
    taken: bool


class ExpectedSupplementItem(BaseModel):
    supplement_id: str
    supplement_name: str
    objective_key: Optional[str] = None
    objective_label: Optional[str] = None
    timing: Optional[str] = None
    dosage: Optional[str] = None


class ExpectedSupplementGroup(BaseModel):
    id: str
    name: str
    taken: bool = False
    timing: Optional[str] = None
    dosage: Optional[str] = None
    items: List[ExpectedSupplementItem] = Field(default_factory=list)


class ProgressResponse(BaseModel):
    selected_date: str
    today_progress: int
    supplements_taken: int
    supplements_total: int
    weekly_data: List[WeeklyProgressItem] = Field(default_factory=list)
    weekly_completion_data: List[WeeklyCompletionPoint] = Field(default_factory=list)
    adherence_data: List[bool] = Field(default_factory=list)
    evolution_data: List[EvolutionPoint] = Field(default_factory=list)
    monthly_data: List[MonthlyHeatmapCell] = Field(default_factory=list)
    daily_intakes: List[DailyIntakeItem] = Field(default_factory=list)
    recommendation_id: Optional[str] = None
    expected_supplements: List[ExpectedSupplementGroup] = Field(default_factory=list)


class DashboardResponse(BaseModel):
    user_name: str
    today_progress: int
    supplements_taken: int
    supplements_total: int
    weekly_data: List[WeeklyProgressItem] = Field(default_factory=list)
    adherence_data: List[bool] = Field(default_factory=list)


class HomeQuestionResponse(BaseModel):
    id: str
    supplement_id: str
    supplement_name: str
    category: str
    question: str
    answer: str


class CurrentRecommendationSnapshotResponse(BaseModel):
    user_id: str
    source: Optional[str] = None
    input: Dict[str, Any] = Field(default_factory=dict)
    derived_input: Dict[str, Any] = Field(default_factory=dict)
    decision: Dict[str, Any] = Field(default_factory=dict)
    saved_recommendation_id: Optional[str] = None
    saved_at: Optional[datetime] = None
    intakes: List[RecommendationIntakeResponse] = Field(default_factory=list)


GOAL_LABEL_BY_ID: Dict[str, str] = {
    option["id"]: option["label"]
    for option in goal_options()
    if isinstance(option, dict)
    and isinstance(option.get("id"), str)
    and isinstance(option.get("label"), str)
}


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

    raw_goals = _clean_text_list(profile.get("goals"))
    canonical_goals = canonicalize_goal_list(raw_goals)

    raw_symptomes = _dedupe_keep_order(
        _clean_text_list(profile.get("symptomes"))
        + _clean_text_list(profile.get("symptoms"))
        + _clean_text_list(personal.get("symptomes"))
        + _clean_text_list(personal.get("symptoms"))
    )
    raw_symptome_goals = canonicalize_goal_list(raw_symptomes)

    canonical_goal_union = _dedupe_keep_order(canonical_goals + raw_symptome_goals)
    symptomes_from_goals = symptoms_for_goals(canonical_goal_union)

    free_text_symptomes = [s for s in raw_symptomes if not canonicalize_goal(s)]
    symptomes = _dedupe_keep_order(symptomes_from_goals + free_text_symptomes)

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
        "goals": canonical_goal_union,
        "symptomes": symptomes,
        "conditions_medicales": conditions_medicales,
    }


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _now_app() -> datetime:
    return _now_utc().astimezone(APP_TIME_ZONE)


def _today_app() -> date:
    return _now_app().date()


def _normalize_email(email: EmailStr | str) -> str:
    return str(email).strip().lower()


async def _find_user_by_email(
    db: AsyncIOMotorDatabase, email: EmailStr | str
) -> Optional[Dict[str, Any]]:
    normalized_email = _normalize_email(email)
    if not normalized_email:
        return None

    return await db.users.find_one(
        {
            "email": {
                "$regex": f"^{re.escape(normalized_email)}$",
                "$options": "i",
            }
        }
    )


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


def _to_app_datetime(value: Optional[datetime]) -> datetime:
    return _to_utc_datetime(value).astimezone(APP_TIME_ZONE)


_WEEKDAY_LETTERS_FR = ["L", "M", "M", "J", "V", "S", "D"]  # Monday..Sunday


def _weekday_letter_fr(value: date) -> str:
    try:
        return _WEEKDAY_LETTERS_FR[value.weekday()]
    except Exception:
        return "?"


def _infer_timing(value: Any) -> str:
    normalized = str(value).lower() if value is not None else ""
    has_morning = "morning" in normalized or "matin" in normalized
    has_evening = (
        "evening" in normalized
        or "night" in normalized
        or "soir" in normalized
        or "nuit" in normalized
    )

    if has_morning and has_evening:
        return "both"
    if has_morning:
        return "morning"
    if has_evening:
        return "evening"
    return "unspecified"


def _format_time_hhmm(value: datetime) -> str:
    dt = _to_app_datetime(value)
    return dt.strftime("%H:%M")


def _parse_anchor_date(date_str: Optional[str]) -> date:
    if not date_str:
        return _today_app()
    try:
        return date.fromisoformat(date_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date, expected YYYY-MM-DD")


def _extract_expected_supplement_groups(decision_payload: Dict[str, Any]) -> List[ExpectedSupplementGroup]:
    groups: Dict[str, ExpectedSupplementGroup] = {}
    if not isinstance(decision_payload, dict):
        return []

    raw_grouped = decision_payload.get("recommendations_by_goal")
    if not isinstance(raw_grouped, dict):
        return []

    for raw_goal_key, raw_items in raw_grouped.items():
        goal_key = _normalize_objective_key(raw_goal_key if isinstance(raw_goal_key, str) else None)
        if not goal_key or not isinstance(raw_items, list):
            continue

        objective_label = GOAL_LABEL_BY_ID.get(goal_key, goal_key)

        for index, raw_item in enumerate(raw_items):
            if not isinstance(raw_item, dict):
                continue

            supplement_name = _clean_optional_text(_recommendation_item_product_name(raw_item))
            if not supplement_name:
                continue

            supplement_name = _repair_mojibake(supplement_name)
            group_id = _fold_text(supplement_name) or supplement_name.casefold()

            raw_id = (
                _clean_optional_text(raw_item.get("id"))
                or _clean_optional_text(raw_item.get("_id"))
                or _clean_optional_text(raw_item.get("code"))
                or str(index)
            )
            supplement_id = f"{goal_key}::{raw_id}"

            dosage = _clean_optional_text(
                raw_item.get("posologie")
                or raw_item.get("dosage")
                or raw_item.get("dose")
                or raw_item.get("quantity")
                or raw_item.get("quantite")
            )
            if dosage is not None:
                dosage = _repair_mojibake(dosage)

            timing = _infer_timing(raw_item.get("timing") or raw_item.get("time") or raw_item.get("moment"))

            group = groups.get(group_id)
            if not group:
                group = ExpectedSupplementGroup(
                    id=group_id,
                    name=supplement_name,
                    timing=timing if timing != "unspecified" else None,
                    dosage=dosage,
                    taken=False,
                    items=[],
                )
                groups[group_id] = group
            else:
                # Merge timing/dosage heuristically so the UI can show one chip per supplement.
                existing_timing = group.timing or "unspecified"
                if existing_timing != timing and timing != "unspecified":
                    if existing_timing == "unspecified":
                        group.timing = timing
                    elif existing_timing != "both":
                        group.timing = "both"
                if not group.dosage and dosage:
                    group.dosage = dosage

            group.items.append(
                ExpectedSupplementItem(
                    supplement_id=supplement_id,
                    supplement_name=supplement_name,
                    objective_key=goal_key,
                    objective_label=objective_label,
                    timing=timing if timing != "unspecified" else None,
                    dosage=dosage,
                )
            )

    # Stable ordering for the UI
    return sorted(groups.values(), key=lambda g: g.name.casefold())


async def _resolve_current_recommendation(
    *,
    db: AsyncIOMotorDatabase,
    user: Dict[str, Any],
    force_refresh: bool = False,
) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
    user_id = user["_id"]
    previous_recommendation = await db.recommendations.find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)],
    )

    profile = user.get("profile") or {}
    prepared = _decision_input_from_profile(profile if isinstance(profile, dict) else {})

    should_refresh = force_refresh or previous_recommendation is None
    if previous_recommendation and not should_refresh:
        user_updated_at = user.get("updated_at")
        recommendation_created_at = previous_recommendation.get("created_at")
        if isinstance(user_updated_at, datetime) and isinstance(recommendation_created_at, datetime):
            should_refresh = _to_utc_datetime(recommendation_created_at) < _to_utc_datetime(user_updated_at)

    if not should_refresh:
        return previous_recommendation, prepared

    if not prepared.get("symptomes"):
        return previous_recommendation, prepared

    decision_payload = await run_in_threadpool(
        decide_rules,
        prepared["symptomes"],
        prepared.get("conditions_medicales") or [],
    )
    decision_payload = _with_best_decision_complement_times(
        decision_payload if isinstance(decision_payload, dict) else {}
    )
    decision_payload = _augment_decision_with_goal_groups(decision_payload, prepared)
    saved = await save_recommendation(
        db,
        user_id=user_id,
        source="profile",
        input_payload=prepared,
        decision_payload=decision_payload,
    )

    if previous_recommendation and previous_recommendation.get("_id") != saved.get("_id"):
        await _carry_over_recommendation_intakes(
            db=db,
            user_id=user_id,
            from_recommendation_id=previous_recommendation["_id"],
            to_recommendation_id=saved["_id"],
            decision_payload=saved.get("decision", decision_payload),
        )
        refreshed = await db.recommendations.find_one({"_id": saved["_id"]})
        return (refreshed or saved), prepared

    return saved, prepared


async def _build_progress_response_payload(
    *,
    db: AsyncIOMotorDatabase,
    user: Dict[str, Any],
    anchor: date,
) -> Dict[str, Any]:
    user_id = user["_id"]
    recommendation, prepared = await _resolve_current_recommendation(db=db, user=user)

    expected_groups: List[ExpectedSupplementGroup] = []
    recommendation_id: Optional[str] = None
    if recommendation:
        recommendation_id = str(recommendation["_id"])
        input_payload = recommendation.get("input", {}) if isinstance(recommendation, dict) else {}
        if not isinstance(input_payload, dict) or not input_payload:
            input_payload = prepared
        decision_payload = recommendation.get("decision", {}) if isinstance(recommendation, dict) else {}
        decision_payload = _with_best_decision_complement_times(decision_payload)
        decision_payload = _augment_decision_with_goal_groups(decision_payload, input_payload)
        expected_groups = _extract_expected_supplement_groups(decision_payload)

    expected_keys = {g.id for g in expected_groups}
    total = len(expected_keys)

    # Fetch the last 30 days of intake events using Europe/Paris day boundaries,
    # then compute per-day states from the latest event.
    start_day = anchor - timedelta(days=29)
    start_dt = datetime.combine(start_day, time.min, tzinfo=APP_TIME_ZONE).astimezone(timezone.utc)
    end_dt = datetime.combine(anchor + timedelta(days=1), time.min, tzinfo=APP_TIME_ZONE).astimezone(timezone.utc)

    cursor = (
        db.recommendation_intakes
        .find({"user_id": user_id, "taken_at": {"$gte": start_dt, "$lt": end_dt}})
        .sort("taken_at", 1)
        .limit(10000)
    )
    docs = await cursor.to_list(length=10000)

    # date -> key -> (taken_at, taken)
    latest_state: Dict[date, Dict[str, Tuple[datetime, bool]]] = {}
    daily_events: List[DailyIntakeItem] = []

    for doc in docs:
        taken_at_raw = doc.get("taken_at")
        if not isinstance(taken_at_raw, datetime):
            continue

        taken_at = _to_utc_datetime(taken_at_raw)
        taken_at_local = taken_at.astimezone(APP_TIME_ZONE)
        day = taken_at_local.date()

        raw_name = doc.get("supplement_name")
        if not isinstance(raw_name, str):
            continue

        supplement_name = _repair_mojibake(raw_name.strip())
        if not supplement_name:
            continue

        key = _fold_text(supplement_name) or supplement_name.casefold()

        # Track only expected supplements for the computed progress.
        if expected_keys and key not in expected_keys:
            continue

        taken = bool(doc.get("taken", False))

        day_map = latest_state.setdefault(day, {})
        previous = day_map.get(key)
        if previous is None or taken_at > previous[0]:
            day_map[key] = (taken_at, taken)

        if day == anchor:
            daily_events.append(
                DailyIntakeItem(
                    time=_format_time_hhmm(taken_at_local),
                    name=supplement_name,
                    taken=taken,
                )
            )

    daily_events.sort(key=lambda item: item.time)

    def taken_count_for_day(day: date) -> int:
        if total == 0:
            return 0
        states = latest_state.get(day, {})
        count = 0
        for key in expected_keys:
            entry = states.get(key)
            if entry and entry[1]:
                count += 1
        return count

    def percent_for_day(day: date) -> int:
        if total == 0:
            return 0
        pct = round(taken_count_for_day(day) / total * 100)
        return int(max(0, min(100, pct)))

    taken_today = taken_count_for_day(anchor)
    today_progress = percent_for_day(anchor)

    weekly_data: List[WeeklyProgressItem] = []
    weekly_completion_data: List[WeeklyCompletionPoint] = []
    for i in range(6, -1, -1):
        day = anchor - timedelta(days=i)
        percent = percent_for_day(day)
        weekly_data.append(
            WeeklyProgressItem(
                day=_weekday_letter_fr(day),
                completed=total > 0 and taken_count_for_day(day) >= total,
            )
        )
        weekly_completion_data.append(
            WeeklyCompletionPoint(
                day=_weekday_letter_fr(day),
                ymd=day.isoformat(),
                percent=percent,
            )
        )

    evolution_data: List[EvolutionPoint] = []
    for i in range(9, -1, -1):
        day = anchor - timedelta(days=i)
        evolution_data.append(
            EvolutionPoint(
                day=10 - i,
                value=percent_for_day(day),
            )
        )

    monthly_data: List[MonthlyHeatmapCell] = []
    for i in range(29, -1, -1):
        day = anchor - timedelta(days=i)
        pct = percent_for_day(day)
        if pct == 0:
            intensity = 0
        elif pct < 50:
            intensity = 1
        elif pct < 100:
            intensity = 2
        else:
            intensity = 3
        monthly_data.append(MonthlyHeatmapCell(day=30 - i, intensity=intensity))

    expected_out: List[ExpectedSupplementGroup] = []
    today_states = latest_state.get(anchor, {})
    for group in expected_groups:
        entry = today_states.get(group.id)
        expected_out.append(
            group.model_copy(
                update={"taken": bool(entry and entry[1])},
            )
        )

    return {
        "selected_date": anchor.isoformat(),
        "today_progress": today_progress,
        "supplements_taken": taken_today,
        "supplements_total": total,
        "weekly_data": weekly_data,
        "weekly_completion_data": weekly_completion_data,
        "adherence_data": [item.completed for item in weekly_data],
        "evolution_data": evolution_data,
        "monthly_data": monthly_data,
        "daily_intakes": daily_events,
        "recommendation_id": recommendation_id,
        "expected_supplements": expected_out,
    }


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


def _augment_decision_with_goal_groups(
    decision_payload: Dict[str, Any],
    input_payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if not isinstance(decision_payload, dict):
        return {}

    decision = dict(decision_payload)

    input_record = input_payload if isinstance(input_payload, dict) else {}
    profile_goals = canonicalize_goal_list(_clean_text_list(input_record.get("goals")))
    decision_goals = canonicalize_goal_list(_clean_text_list(decision.get("goals")))
    selected_goals = _dedupe_keep_order(profile_goals + decision_goals)

    recommendations = decision.get("recommendations")
    if not isinstance(recommendations, list):
        if selected_goals:
            decision["goals"] = selected_goals
            decision["recommendations_by_goal"] = {goal: [] for goal in selected_goals}
        return decision

    recommendations_copy: List[Any] = []
    grouped: Dict[str, List[Dict[str, Any]]] = {goal: [] for goal in selected_goals}
    selected_goal_set = set(selected_goals)

    for item in recommendations:
        if not isinstance(item, dict):
            recommendations_copy.append(item)
            continue

        item_copy = dict(item)
        explicit_goal_values = (
            _clean_text_list(item_copy.get("goals"))
            + _clean_text_list(item_copy.get("objectifs"))
        )
        for maybe_goal in [item_copy.get("goal"), item_copy.get("objectif")]:
            if isinstance(maybe_goal, str) and maybe_goal.strip():
                explicit_goal_values.append(maybe_goal.strip())

        explicit_goals = canonicalize_goal_list(explicit_goal_values)
        covered_goals: List[str] = []
        for symptom in (
            _clean_text_list(item_copy.get("symptomes_couverts"))
            + _clean_text_list(item_copy.get("covered_symptoms"))
        ):
            covered_goals.extend(canonical_goals_for_symptom(symptom))

        item_goals = _dedupe_keep_order(explicit_goals + covered_goals)
        if selected_goal_set:
            item_goals = [goal for goal in item_goals if goal in selected_goal_set]
        if item_goals:
            item_copy["goals"] = item_goals
            item_copy["goal"] = item_goals[0]

        recommendations_copy.append(item_copy)
        for goal in item_goals:
            grouped.setdefault(goal, []).append(item_copy)

    decision["recommendations"] = recommendations_copy

    selected_goal_union = _dedupe_keep_order(selected_goals + list(grouped.keys()))
    if selected_goal_union:
        decision["goals"] = selected_goal_union
        decision["recommendations_by_goal"] = {
            goal: grouped.get(goal, []) for goal in selected_goal_union
        }

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
    input_payload = doc.get("input", {}) if isinstance(doc, dict) else {}
    decision = _with_best_decision_complement_times(doc.get("decision", {}))
    decision = _augment_decision_with_goal_groups(decision, input_payload)
    return {
        "id": str(doc["_id"]),
        "user_id": str(doc["user_id"]),
        "source": doc.get("source", "profile"),
        "input": input_payload,
        "decision": decision,
        "created_at": doc.get("created_at"),
    }


def _clean_optional_text(value: Optional[str]) -> Optional[str]:
    if not isinstance(value, str):
        return None
    txt = value.strip()
    return txt if txt else None


def _coerce_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        txt = value.strip().casefold()
        if txt in {"true", "1", "yes", "oui"}:
            return True
        if txt in {"false", "0", "no", "non", ""}:
            return False
    return default


def _parse_optional_datetime_input(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        txt = value.strip()
        if not txt:
            return None
        if txt.endswith("Z"):
            txt = f"{txt[:-1]}+00:00"
        try:
            return datetime.fromisoformat(txt)
        except Exception:
            return None
    return None


def _normalize_objective_key(value: Optional[str]) -> Optional[str]:
    txt = _clean_optional_text(value)
    if not txt:
        return None
    canonical = canonicalize_goal(txt)
    if canonical:
        return canonical
    return txt.casefold()


def _build_intake_targets_from_decision(
    decision_payload: Dict[str, Any],
) -> Dict[Tuple[str, str], Dict[str, str]]:
    targets: Dict[Tuple[str, str], Dict[str, str]] = {}
    if not isinstance(decision_payload, dict):
        return targets

    grouped = decision_payload.get("recommendations_by_goal")
    if not isinstance(grouped, dict):
        return targets

    for raw_goal_key, raw_items in grouped.items():
        goal_key = _normalize_objective_key(raw_goal_key if isinstance(raw_goal_key, str) else None)
        if not goal_key or not isinstance(raw_items, list):
            continue

        objective_label = GOAL_LABEL_BY_ID.get(goal_key, goal_key)

        for index, raw_item in enumerate(raw_items):
            if not isinstance(raw_item, dict):
                continue

            supplement_name = _clean_optional_text(_recommendation_item_product_name(raw_item))
            if not supplement_name:
                continue

            raw_id = (
                _clean_optional_text(raw_item.get("id"))
                or _clean_optional_text(raw_item.get("_id"))
                or _clean_optional_text(raw_item.get("code"))
                or str(index)
            )
            key = (goal_key, supplement_name.casefold())
            if key in targets:
                continue

            targets[key] = {
                "supplement_id": f"{goal_key}::{raw_id}",
                "supplement_name": supplement_name,
                "objective_key": goal_key,
                "objective_label": objective_label,
            }

    return targets


def _build_carried_intake_docs(
    *,
    previous_intakes: List[Dict[str, Any]],
    targets: Dict[Tuple[str, str], Dict[str, str]],
    user_id: ObjectId,
    recommendation_id: ObjectId,
) -> List[Dict[str, Any]]:
    if not previous_intakes or not targets:
        return []

    now = _now_utc()
    docs: List[Dict[str, Any]] = []
    seen: set[Tuple[str, str]] = set()

    for intake in previous_intakes:
        supplement_name = _clean_optional_text(intake.get("supplement_name"))
        if not supplement_name:
            continue

        objective_key = _normalize_objective_key(intake.get("objective_key"))
        if not objective_key:
            supplement_id = _clean_optional_text(intake.get("supplement_id"))
            if supplement_id and "::" in supplement_id:
                objective_key = _normalize_objective_key(supplement_id.split("::", 1)[0])
        if not objective_key:
            continue

        key = (objective_key, supplement_name.casefold())
        if key in seen:
            continue

        target = targets.get(key)
        if not target:
            continue
        seen.add(key)

        taken_at_raw = intake.get("taken_at")
        taken_at = _to_utc_datetime(taken_at_raw if isinstance(taken_at_raw, datetime) else None)

        docs.append(
            {
                "user_id": user_id,
                "recommendation_id": recommendation_id,
                "supplement_id": target["supplement_id"],
                "supplement_name": target["supplement_name"],
                "objective_key": target["objective_key"],
                "objective_label": target["objective_label"],
                "taken": bool(intake.get("taken", False)),
                "taken_at": taken_at,
                "created_at": now,
            }
        )

    return docs


async def _carry_over_recommendation_intakes(
    *,
    db: AsyncIOMotorDatabase,
    user_id: ObjectId,
    from_recommendation_id: ObjectId,
    to_recommendation_id: ObjectId,
    decision_payload: Dict[str, Any],
) -> int:
    if from_recommendation_id == to_recommendation_id:
        return 0

    existing = await db.recommendation_intakes.find_one(
        {"user_id": user_id, "recommendation_id": to_recommendation_id}
    )
    if existing:
        return 0

    targets = _build_intake_targets_from_decision(decision_payload)
    if not targets:
        return 0

    previous_intakes = await (
        db.recommendation_intakes
        .find({"user_id": user_id, "recommendation_id": from_recommendation_id})
        .sort([("taken_at", -1), ("created_at", -1)])
        .to_list(length=2000)
    )
    if not previous_intakes:
        return 0

    carried_docs = _build_carried_intake_docs(
        previous_intakes=previous_intakes,
        targets=targets,
        user_id=user_id,
        recommendation_id=to_recommendation_id,
    )
    if not carried_docs:
        return 0

    await db.recommendation_intakes.insert_many(carried_docs)
    return len(carried_docs)


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
    decision_payload = _augment_decision_with_goal_groups(decision_payload, input_payload)
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


@app.get("/meta/goals", response_model=List[GoalOptionResponse])
async def list_goal_options():
    return goal_options()


@app.get("/dashboard", response_model=DashboardResponse)
async def dashboard(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user),
):
    profile = user.get("profile") or {}
    personal = profile.get("personal") if isinstance(profile, dict) else {}
    personal = personal if isinstance(personal, dict) else {}
    raw_first_name = (
        personal.get("first_name")
        or profile.get("first_name")
        or personal.get("name")
        or profile.get("name")
        or ""
    )
    if not isinstance(raw_first_name, str):
        raw_first_name = ""
    name = raw_first_name.strip()
    user_name = name.split(" ", 1)[0] if name else "vous"

    payload = await _build_progress_response_payload(db=db, user=user, anchor=_today_app())

    return {
        "user_name": user_name,
        "today_progress": payload["today_progress"],
        "supplements_taken": payload["supplements_taken"],
        "supplements_total": payload["supplements_total"],
        "weekly_data": payload["weekly_data"],
        "adherence_data": payload["adherence_data"],
    }


@app.get(
    "/dashboard/random-questions",
    response_model=List[HomeQuestionResponse],
)
async def dashboard_random_questions(
    limit: int = 4,
    user: Dict[str, Any] = Depends(get_current_user),
):
    _ = user
    return _build_home_questions(limit=limit)


@app.get(
    "/users/me/current-recommendation",
    response_model=CurrentRecommendationSnapshotResponse,
)
async def get_current_recommendation_snapshot(
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user),
):
    recommendation, prepared = await _resolve_current_recommendation(db=db, user=user)

    if not recommendation:
        return {
            "user_id": str(user["_id"]),
            "derived_input": prepared,
            "input": prepared,
            "decision": {},
            "saved_recommendation_id": None,
            "saved_at": None,
            "source": None,
            "intakes": [],
        }

    recommendation_id = recommendation["_id"]
    recommendation_public_data = recommendation_public(recommendation)
    intakes_cursor = (
        db.recommendation_intakes
        .find({"recommendation_id": recommendation_id, "user_id": user["_id"]})
        .sort("taken_at", -1)
        .limit(500)
    )
    intake_docs = await intakes_cursor.to_list(length=500)

    return {
        "user_id": str(user["_id"]),
        "source": recommendation_public_data.get("source"),
        "input": recommendation_public_data.get("input", {}),
        "derived_input": prepared,
        "decision": recommendation_public_data.get("decision", {}),
        "saved_recommendation_id": recommendation_public_data.get("id"),
        "saved_at": recommendation_public_data.get("created_at"),
        "intakes": [recommendation_intake_public(doc) for doc in intake_docs],
    }


@app.get("/tracking/progress", response_model=ProgressResponse)
async def tracking_progress(
    date: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user),
):
    anchor = _parse_anchor_date(date)
    return await _build_progress_response_payload(db=db, user=user, anchor=anchor)


def _repair_mojibake(text: str) -> str:
    raw = text or ""
    # Recover common double-encoded legacy payloads, e.g. "Magnésium" -> "Magnésium".
    for _ in range(2):
        if not any(ch in raw for ch in ("Ã", "Â", "â")):
            break
        try:
            repaired = raw.encode("latin-1").decode("utf-8")
        except Exception:
            break
        if repaired == raw:
            break
        raw = repaired
    return raw


def _fold_text(text: str) -> str:
    txt = _repair_mojibake(text or "")
    folded = unicodedata.normalize("NFKD", txt)
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch))
    folded = folded.casefold()
    folded = re.sub(r"[^a-z0-9]+", " ", folded).strip()
    return folded


def _strip_citation_markers(text: str) -> str:
    txt = _repair_mojibake(text or "")
    # e.g. "[12]" markers used throughout the knowledge base.
    txt = re.sub(r"\[[0-9]+\]", "", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def _extract_health_conditions(sheet: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    for entry in (sheet.get("database") or []):
        if not isinstance(entry, dict):
            continue
        value = entry.get("health_condition_or_goal")
        if isinstance(value, str) and value.strip():
            out.append(_repair_mojibake(value.strip()))
    # Keep order but dedupe (case-insensitive)
    seen = set()
    uniq: List[str] = []
    for item in out:
        key = item.casefold()
        if key in seen:
            continue
        seen.add(key)
        uniq.append(item)
    return uniq


_ENCYCLO_CATEGORIES: List[Tuple[str, Tuple[str, ...]]] = [
    ("Cognition", ("cognit", "memoire", "memory", "attention", "adhd", "alzheimer", "dement", "brain")),
    ("Cardiovasculaire", ("cardio", "coeur", "heart", "vascular", "hypertens", "cholesterol", "triglycer", "atheroscler")),
    ("Immunité", ("immun", "infection", "rhume", "grippe", "respir", "cold", "flu")),
    ("Vision", ("vision", "oeil", "eye", "retin", "macul", "glaucom", "cataract")),
    ("Os & Articulations", ("os", "bone", "articul", "joint", "osteopor", "arthrit", "cartilage")),
]


def _encyclo_category_for_sheet(sheet: Dict[str, Any]) -> str:
    # Heuristic mapping so the UI "entry point cards" can filter consistently.
    cond_text = " ".join(_extract_health_conditions(sheet))
    hay = _fold_text(f"{sheet.get('name','')} {sheet.get('description','')} {cond_text}")
    for label, keywords in _ENCYCLO_CATEGORIES:
        if any(k in hay for k in keywords):
            return label
    return "Autres"


_MOLECULE_ABBR_STOP = {
    "RDA",
    "UL",
    "AI",
    "DOI",
    "NHANES",
    "RCT",
    "CRP",
    "HDL",
    "LDL",
    "ATP",
    "CYP",
}


def _extract_molecules(sheet: Dict[str, Any]) -> List[str]:
    texts: List[str] = []
    for key in ("description", "dosage"):
        value = sheet.get(key)
        if isinstance(value, str) and value.strip():
            texts.append(value)

    overview = sheet.get("overview")
    if isinstance(overview, list) and overview:
        first = overview[0] if isinstance(overview[0], dict) else None
        if first and isinstance(first.get("answer"), str):
            texts.append(first["answer"])

    candidates: List[str] = []

    for raw in texts:
        txt = _repair_mojibake(raw)

        # A) All-caps abbreviations (EPA, DHA...)
        for token in re.findall(r"\b[A-Z]{2,5}\b", txt):
            if token in _MOLECULE_ABBR_STOP:
                continue
            if token not in candidates:
                candidates.append(token)

        # B) Short parenthetical chemical names (cholécalciférol, ergocalciférol...)
        for inside in re.findall(r"\(([A-Za-zÀ-ÖØ-öø-ÿ][^)]{0,40})\)", txt):
            cleaned = inside.strip()
            if len(cleaned) > 30:
                continue
            if any(ch.isdigit() for ch in cleaned):
                continue
            if cleaned.count(" ") > 2:
                continue
            cleaned = _repair_mojibake(cleaned)
            if cleaned and cleaned not in candidates:
                candidates.append(cleaned)

    name = sheet.get("name")
    if isinstance(name, str) and name.strip():
        fallback = _repair_mojibake(name.strip())
    else:
        fallback = "Supplement"

    if not candidates:
        return [fallback]

    # Keep it readable in the UI: a few tags max.
    return candidates[:4]


def _extract_benefits(sheet: Dict[str, Any]) -> List[str]:
    overview = sheet.get("overview")
    if not isinstance(overview, list):
        return []

    for item in overview:
        if not isinstance(item, dict):
            continue
        q = item.get("question")
        a = item.get("answer")
        if not (isinstance(q, str) and isinstance(a, str)):
            continue

        q_fold = _fold_text(q)
        if "bienfait" not in q_fold and "avantage" not in q_fold and "benefit" not in q_fold:
            continue

        answer = _strip_citation_markers(a)
        # Split into short-ish bullet points (first 4 meaningful sentences).
        parts = re.split(r"(?<=[.!?])\\s+", answer)
        out: List[str] = []
        for part in parts:
            txt = part.strip()
            if len(txt) < 20:
                continue
            out.append(txt)
            if len(out) >= 4:
                break
        return out

    return []


def _extract_sources(sheet: Dict[str, Any], limit: int = 8) -> List[str]:
    refs = sheet.get("references")
    if not isinstance(refs, list):
        return []

    out: List[str] = []
    for ref in refs:
        if not isinstance(ref, dict):
            continue
        text = ref.get("text") or ref.get("title") or ref.get("citation")
        if not isinstance(text, str):
            continue
        txt = _repair_mojibake(text.strip())
        if not txt:
            continue
        out.append(txt)
        if len(out) >= limit:
            break
    return out


def _supplement_summary_from_sheet(sheet: Dict[str, Any]) -> EncyclopedieSupplementSummaryResponse | None:
    slug = sheet.get("slug")
    name = sheet.get("name")
    description = sheet.get("description")
    if not (isinstance(slug, str) and slug.strip()):
        return None
    if not (isinstance(name, str) and name.strip()):
        return None
    if not isinstance(description, str):
        description = ""

    return EncyclopedieSupplementSummaryResponse(
        id=slug.strip(),
        name=_repair_mojibake(name.strip()),
        category=_encyclo_category_for_sheet(sheet),
        description=_repair_mojibake(description.strip()),
        molecules=_extract_molecules(sheet),
    )


def _supplement_detail_from_sheet(sheet: Dict[str, Any]) -> EncyclopedieSupplementDetailResponse | None:
    summary = _supplement_summary_from_sheet(sheet)
    if not summary:
        return None

    dosage = sheet.get("dosage")
    dosage_out: Optional[str] = None
    if isinstance(dosage, str) and dosage.strip():
        # Avoid very large payloads for extremely long knowledge entries.
        dosage_out = _repair_mojibake(dosage.strip())[:2000]

    return EncyclopedieSupplementDetailResponse(
        **summary.model_dump(),
        benefits=_extract_benefits(sheet),
        dosage=dosage_out,
        sources=_extract_sources(sheet, limit=10),
    )


def _extract_home_overview_pairs(sheet: Dict[str, Any], limit: int = 8) -> List[Tuple[str, str]]:
    overview = sheet.get("overview")
    if not isinstance(overview, list):
        return []

    pairs: List[Tuple[str, str]] = []
    for item in overview:
        if not isinstance(item, dict):
            continue

        raw_question = item.get("question")
        raw_answer = item.get("answer")
        if not isinstance(raw_question, str) or not isinstance(raw_answer, str):
            continue

        question = _strip_citation_markers(raw_question).strip(" -•")
        answer = _strip_citation_markers(raw_answer)
        if len(question) < 8 or len(answer) < 20:
            continue

        pairs.append((question, answer))
        if len(pairs) >= limit:
            break

    return pairs


def _build_home_questions(limit: int = 4) -> List[HomeQuestionResponse]:
    sheets = CATALOGUE_COMPLET.get("complement_alimentaire") or []
    candidates: List[HomeQuestionResponse] = []

    for sheet in sheets:
        if not isinstance(sheet, dict):
            continue

        summary = _supplement_summary_from_sheet(sheet)
        if not summary:
            continue

        for index, (question, answer) in enumerate(_extract_home_overview_pairs(sheet), start=1):
            candidates.append(
                HomeQuestionResponse(
                    id=f"{summary.id}-{index}",
                    supplement_id=summary.id,
                    supplement_name=summary.name,
                    category=summary.category,
                    question=question,
                    answer=answer.strip(),
                )
            )

    if not candidates:
        return []

    safe_limit = max(1, min(limit, 8))
    if len(candidates) <= safe_limit:
        return candidates

    return random.sample(candidates, safe_limit)


@app.get(
    "/encyclopedie/supplements",
    response_model=List[EncyclopedieSupplementSummaryResponse],
)
async def list_encyclopedie_supplements(
    q: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 40,
    offset: int = 0,
):
    limit = max(1, min(limit, 200))
    offset = max(0, offset)

    sheets = CATALOGUE_COMPLET.get("complement_alimentaire") or []

    q_fold = _fold_text(q or "")
    category_fold = _fold_text(category or "")

    items: List[EncyclopedieSupplementSummaryResponse] = []
    for sheet in sheets:
        if not isinstance(sheet, dict):
            continue

        summary = _supplement_summary_from_sheet(sheet)
        if not summary:
            continue

        if category_fold and _fold_text(summary.category) != category_fold:
            continue

        if q_fold:
            cond_text = " ".join(_extract_health_conditions(sheet))
            hay = _fold_text(
                f"{summary.id} {summary.name} {summary.description} {cond_text}"
            )
            if q_fold not in hay:
                continue

        items.append(summary)

    items.sort(key=lambda item: item.name.casefold())
    return items[offset : offset + limit]


@app.get(
    "/encyclopedie/supplements/{supplement_id}",
    response_model=EncyclopedieSupplementDetailResponse,
)
async def get_encyclopedie_supplement(supplement_id: str):
    supp_key = (supplement_id or "").strip()
    if not supp_key:
        raise HTTPException(status_code=400, detail="Invalid supplement id")

    sheets = CATALOGUE_COMPLET.get("complement_alimentaire") or []
    for sheet in sheets:
        if not isinstance(sheet, dict):
            continue
        slug = sheet.get("slug")
        if isinstance(slug, str) and slug.strip() == supp_key:
            detail = _supplement_detail_from_sheet(sheet)
            if not detail:
                break
            return detail

    raise HTTPException(status_code=404, detail="Supplement not found")


@app.get("/auth/check-email", response_model=EmailAvailabilityResponse)
async def check_email_availability(
    email: EmailStr, db: AsyncIOMotorDatabase = Depends(get_db)
):
    normalized_email = _normalize_email(email)
    existing = await _find_user_by_email(db, normalized_email)

    return {
        "available": existing is None,
        "normalized_email": normalized_email,
        "reason": "already_exists" if existing else None,
        "suggestion": None,
    }


@app.post("/auth/signup", response_model=TokenResponse)
async def signup(req: SignupRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    normalized_email = _normalize_email(req.email)
    existing = await _find_user_by_email(db, normalized_email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    now = _now_utc()
    user_doc = {
        "email": normalized_email,
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
    user = await _find_user_by_email(db, req.email)
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

    if isinstance(data.get("goals"), list):
        data["goals"] = canonicalize_goal_list(_clean_text_list(data.get("goals")))

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
    recommendation, prepared = await _resolve_current_recommendation(
        db=db,
        user=user,
        force_refresh=True,
    )

    if not recommendation or not prepared["symptomes"]:
        raise HTTPException(
            status_code=400,
            detail=(
                "No usable symptoms/goals found in your profile. "
                "Update `profile.goals` or `profile.personal.symptomes` first."
            ),
        )

    recommendation_public_data = recommendation_public(recommendation)

    return {
        "user_id": str(user["_id"]),
        "derived_input": prepared,
        "decision": recommendation_public_data["decision"],
        "saved_recommendation_id": recommendation_public_data["id"],
        "saved_at": recommendation_public_data["created_at"],
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

    input_payload = recommendation.get("input", {}) if isinstance(recommendation, dict) else {}
    decision = _with_best_decision_complement_times(
        recommendation.get("decision", {}) if isinstance(recommendation, dict) else {}
    )
    decision = _augment_decision_with_goal_groups(decision, input_payload)
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

        taken_at = _to_utc_datetime(_parse_optional_datetime_input(intake.taken_at))
        intake_doc = {
            "user_id": user["_id"],
            "recommendation_id": rec_id,
            "supplement_id": _clean_optional_text(intake.supplement_id),
            "supplement_name": supplement_name,
            "objective_key": _clean_optional_text(intake.objective_key),
            "objective_label": _clean_optional_text(intake.objective_label),
            "taken": _coerce_bool(intake.taken, default=True),
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
        "decision": _augment_decision_with_goal_groups(
            _with_best_decision_complement_times(updated_recommendation.get("decision", {})),
            updated_recommendation.get("input", {}) if isinstance(updated_recommendation, dict) else {},
        ),
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
    decision = _augment_decision_with_goal_groups(
        decision,
        item.get("input", {}) if isinstance(item, dict) else {},
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
