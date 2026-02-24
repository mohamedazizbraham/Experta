from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Optional, Set

from database import CATALOGUE_COMPLET
from logic import normalize_health_condition


def _fold_text(value: str) -> str:
    raw = value or ""
    folded = unicodedata.normalize("NFKD", raw)
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch))
    folded = re.sub(r"[^a-z0-9]+", " ", folded.lower()).strip()
    return folded


GOAL_SPECS: List[Dict[str, Any]] = [
    {
        "id": "sleep_support",
        "label": "Ameliorer mon sommeil",
        "symptom_candidates": ["sommeil", "insomnie", "sleep"],
        "aliases": [
            "sleep_support",
            "sleep support",
            "sleep health",
            "sante du sommeil",
            "sommeil",
            "insomnie",
            "insomnia",
            "ameliorer mon sommeil",
            "narcolepsy",
            "terreurs nocturnes",
        ],
    },
    {
        "id": "stress_anxiety_support",
        "label": "Gerer le stress et l'anxiete",
        "symptom_candidates": ["stress", "anxiete", "trouble"],
        "aliases": [
            "stress_anxiety_support",
            "stress anxiety support",
            "stress",
            "anxiete",
            "anxiety",
            "trouble anxieux",
            "trouble d anxiete generalisee",
            "panic disorder",
            "ptsd",
            "trouble de stress post traumatique",
            "gerer le stress et l anxiete",
        ],
    },
    {
        "id": "mood_depression_support",
        "label": "Ameliorer mon humeur",
        "symptom_candidates": ["depression", "humeur", "mood"],
        "aliases": [
            "mood_depression_support",
            "mood depression support",
            "depression",
            "major depressive disorder",
            "trouble depressif majeur",
            "humeur",
            "mood improvement",
            "amelioration de l humeur",
            "ameliorer mon humeur",
        ],
    },
    {
        "id": "energy_fatigue",
        "label": "Augmenter mon energie",
        "symptom_candidates": ["fatigue", "energie"],
        "aliases": [
            "energy_fatigue",
            "energy fatigue",
            "fatigue",
            "augmenter mon energie",
            "low energy",
            "muscle recovery",
            "recuperation musculaire",
        ],
    },
    {
        "id": "focus_cognition",
        "label": "Ameliorer ma concentration et memoire",
        "symptom_candidates": ["concentration", "cognitive", "memoire"],
        "aliases": [
            "focus_cognition",
            "focus cognition",
            "amelioration cognitive",
            "cognitive improvement",
            "concentration et attention",
            "memoire",
            "attention deficit hyperactivity disorder",
            "ameliorer ma concentration et memoire",
        ],
    },
    {
        "id": "weight_loss",
        "label": "Perdre du poids",
        "symptom_candidates": ["perte", "obesite", "obesity", "surpoids"],
        "aliases": [
            "weight_loss",
            "weight loss",
            "perte de poids",
            "perte de poids et maintien",
            "obesite",
            "obesity",
            "surpoids",
            "prediabetes",
            "syndrome metabolique",
        ],
    },
    {
        "id": "appetite_control",
        "label": "Controler mon appetit",
        "symptom_candidates": ["surpoids", "obesite", "perte"],
        "aliases": [
            "appetite_control",
            "appetite control",
            "controler mon appetit",
            "controle de l appetit",
            "surpoids",
            "obesite",
            "perte de poids",
        ],
    },
    {
        "id": "digestion_gut",
        "label": "Ameliorer ma digestion",
        "symptom_candidates": ["digestive", "intestin", "constipation"],
        "aliases": [
            "digestion_gut",
            "digestion gut",
            "sante digestive",
            "digestive health",
            "constipation",
            "syndrome de l intestin irritable",
            "ibs",
            "reflux gastro oesophagien",
            "ameliorer ma digestion",
        ],
    },
    {
        "id": "immune_support",
        "label": "Renforcer mon immunite",
        "symptom_candidates": ["immunitaire", "grippe", "infection"],
        "aliases": [
            "immune_support",
            "immune support",
            "sante immunitaire",
            "immunite",
            "renforcer mon immunite",
            "infection respiratoire aigue",
            "grippe",
            "rhume",
        ],
    },
    {
        "id": "muscle_gain_strength",
        "label": "Gagner en muscle et force",
        "symptom_candidates": ["taille", "muscle", "force"],
        "aliases": [
            "muscle_gain_strength",
            "muscle gain strength",
            "taille et force musculaires",
            "muscle size strength",
            "gagner en muscle et force",
            "performance athletique generale",
            "muscle recovery",
        ],
    },
    {
        "id": "pain_inflammation",
        "label": "Reduire douleurs et inflammations",
        "symptom_candidates": ["douleur", "arthrose", "arthrite"],
        "aliases": [
            "pain_inflammation",
            "pain inflammation",
            "douleur",
            "douleur chronique",
            "arthrose",
            "osteoarthritis",
            "arthrite",
            "fibromyalgie",
            "reduire douleurs et inflammations",
        ],
    },
    {
        "id": "migraine_headache",
        "label": "Prevenir migraines et maux de tete",
        "symptom_candidates": ["migraine", "cephalee"],
        "aliases": [
            "migraine_headache",
            "migraine headache",
            "migraine",
            "cephalee migraineuse",
            "tinnitus",
            "acouphene",
            "prevenir migraines et maux de tete",
        ],
    },
]


def _known_symptom_tokens_from_catalogue() -> Set[str]:
    tokens: Set[str] = set()
    for category_items in CATALOGUE_COMPLET.values():
        for sheet in category_items:
            database = sheet.get("database")
            if not isinstance(database, list):
                continue
            for entry in database:
                if not isinstance(entry, dict):
                    continue
                value = entry.get("health_condition_or_goal")
                if not isinstance(value, str) or not value.strip():
                    continue
                token = normalize_health_condition(value)
                if token:
                    tokens.add(token)
    return tokens


KNOWN_SYMPTOM_TOKENS = _known_symptom_tokens_from_catalogue()


_GOAL_BY_ID: Dict[str, Dict[str, Any]] = {spec["id"]: spec for spec in GOAL_SPECS}
_ALIAS_TO_GOAL: Dict[str, str] = {}
_SYMPTOM_TO_GOALS: Dict[str, List[str]] = {}

for spec in GOAL_SPECS:
    goal_id = spec["id"]
    aliases = [goal_id, spec["label"], *(spec.get("aliases") or [])]
    for alias in aliases:
        key = _fold_text(alias)
        if key:
            _ALIAS_TO_GOAL[key] = goal_id

    for symptom_candidate in spec.get("symptom_candidates") or []:
        token = normalize_health_condition(symptom_candidate)
        if token:
            goals = _SYMPTOM_TO_GOALS.setdefault(token, [])
            if goal_id not in goals:
                goals.append(goal_id)


def goal_options() -> List[Dict[str, Any]]:
    return [{"id": spec["id"], "label": spec["label"]} for spec in GOAL_SPECS]


def canonicalize_goal(value: str) -> Optional[str]:
    key = _fold_text(value)
    if not key:
        return None

    exact = _ALIAS_TO_GOAL.get(key)
    if exact:
        return exact

    token = normalize_health_condition(value)
    if token and token in _SYMPTOM_TO_GOALS:
        goals = _SYMPTOM_TO_GOALS[token]
        if goals:
            return goals[0]
    return None


def canonicalize_goal_list(values: List[str]) -> List[str]:
    seen: Set[str] = set()
    out: List[str] = []
    for value in values:
        goal_id = canonicalize_goal(value)
        if not goal_id or goal_id in seen:
            continue
        seen.add(goal_id)
        out.append(goal_id)
    return out


def canonical_goal_for_symptom(value: str) -> Optional[str]:
    goals = canonical_goals_for_symptom(value)
    if not goals:
        return None
    return goals[0]


def canonical_goals_for_symptom(value: str) -> List[str]:
    token = normalize_health_condition(value)
    if not token:
        return []
    return list(_SYMPTOM_TO_GOALS.get(token, []))


def symptoms_for_goals(goal_ids: List[str], known_symptoms: Optional[Set[str]] = None) -> List[str]:
    known = known_symptoms if known_symptoms is not None else KNOWN_SYMPTOM_TOKENS
    out: List[str] = []
    seen: Set[str] = set()

    for goal_id in goal_ids:
        spec = _GOAL_BY_ID.get(goal_id)
        if not spec:
            continue

        candidates: List[str] = []
        for raw_candidate in spec.get("symptom_candidates") or []:
            token = normalize_health_condition(raw_candidate)
            if token and token not in candidates:
                candidates.append(token)

        selected: Optional[str] = None
        for token in candidates:
            if token in known:
                selected = token
                break
        if not selected and candidates:
            selected = candidates[0]

        if selected and selected not in seen:
            seen.add(selected)
            out.append(selected)

    return out
