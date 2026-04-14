from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

from database import CATALOGUE_PRODUITS, CONTRE_INDICATIONS, get_product_category_type
from logic import (
    MoteurRecommandation,
    BesoinClient,
    ConditionClient,
    Recommandation,
    ProduitInterdit,
    calculate_recommendation_grade,
    normalize_health_condition,
)

MAX_SUPPLEMENT_RECOMMENDATIONS = 5


def _norm(x: str) -> str:
    return (x or "").strip().lower()


def _norm_symptome(x: str) -> str:
    # IMPORTANT: même normalisation que celle utilisée dans logic.py
    return normalize_health_condition(_norm(x))


def _known_symptomes() -> Set[str]:
    # IMPORTANT: normaliser aussi les symptômes connus, sinon mismatch
    out: Set[str] = set()
    for p in CATALOGUE_PRODUITS:
        cible = p.get("cible")
        if cible:
            out.add(_norm_symptome(cible))
    return out


def _known_conditions() -> Set[str]:
    return {(_norm(c.get("condition", ""))) for c in CONTRE_INDICATIONS if c.get("condition")}


def _recommendation_sort_key(item: Dict[str, Any]) -> Tuple[int, int, str]:
    return (
        -int(item.get("grade_score", 0)),
        -int(item.get("score_symptomes", 0)),
        str(item.get("produit", "")).lower(),
    )


def _limit_supplement_recommendations(recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    limited: List[Dict[str, Any]] = []
    supplement_count = 0

    for item in recommendations:
        if item.get("category_type") == "recommendation":
            if supplement_count >= MAX_SUPPLEMENT_RECOMMENDATIONS:
                continue
            supplement_count += 1
        limited.append(item)

    return limited


def decide(symptomes: List[str], conditions_medicales: Optional[List[str]] = None) -> Dict[str, Any]:
    conditions_medicales = conditions_medicales or []

    symptomes_norm = [_norm_symptome(s) for s in symptomes if _norm(s)]
    conditions_norm = [_norm(c) for c in conditions_medicales if _norm(c)]

    known_s = _known_symptomes()
    known_c = _known_conditions()

    unknown_symptomes = sorted({s for s in symptomes_norm if s not in known_s})
    unknown_conditions = sorted({c for c in conditions_norm if c not in known_c})

    symptomes_use = [s for s in symptomes_norm if s in known_s]
    conditions_use = [c for c in conditions_norm if c in known_c]

    engine = MoteurRecommandation()
    engine.reset()

    for s in symptomes_use:
        engine.declare(BesoinClient(symptome=s))

    for c in conditions_use:
        engine.declare(ConditionClient(condition=c))

    engine.run()

    facts = list(engine.facts.values())

    forbidden: Set[str] = set()
    matches: Set[Tuple[str, str]] = set()

    for f in facts:
        if isinstance(f, ProduitInterdit):
            forbidden.add(f["produit"])
        elif isinstance(f, Recommandation):
            matches.add((f["nom"], f["cible"]))

    matches = {(p, s) for (p, s) in matches if p not in forbidden}

    by_product: Dict[str, Set[str]] = {}
    for p, s in matches:
        by_product.setdefault(p, set()).add(s)

    recommendations: List[Dict[str, Any]] = []
    for produit, covered in by_product.items():
        category_type = get_product_category_type(produit) or "recommendation"
        score_symptomes = len(covered)
        grade_info = {
            "grade": "",
            "grade_score": 0,
            "grade_source": "none",
        }
        if category_type == "recommendation":
            grade_info = calculate_recommendation_grade(produit, sorted(covered))

        recommendations.append(
            {
                "produit": produit,
                "score": score_symptomes,
                "score_symptomes": score_symptomes,
                "symptomes_couverts": sorted(covered),
                "category_type": category_type,
                **grade_info,
            }
        )

    recommendations.sort(key=_recommendation_sort_key)
    recommendations = _limit_supplement_recommendations(recommendations)
    best_decision = recommendations[0] if recommendations else None

    return {
        "input": {
            "symptomes": symptomes,
            "conditions_medicales": conditions_medicales,
            "symptomes_utilises": symptomes_use,
            "conditions_utilisees": conditions_use,
        },
        "best_decision": best_decision,
        "recommendations": recommendations,
        "forbidden_products": sorted(forbidden),
        "unknown_symptomes": unknown_symptomes,
        "unknown_conditions": unknown_conditions,
    }
