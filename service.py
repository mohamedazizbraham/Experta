from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

from database import CATALOGUE_PRODUITS, CONTRE_INDICATIONS
from logic import (
    MoteurRecommandation,
    BesoinClient,
    ConditionClient,
    Recommandation,
    ProduitInterdit,
)


def _norm(x: str) -> str:
    return (x or "").strip().lower()


def _known_symptomes() -> Set[str]:
    return {(_norm(p.get("cible", ""))) for p in CATALOGUE_PRODUITS if p.get("cible")}


def _known_conditions() -> Set[str]:
    return {(_norm(c.get("condition", ""))) for c in CONTRE_INDICATIONS if c.get("condition")}


def decide(symptomes: List[str], conditions_medicales: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Run your existing Experta engine and return:
    - recommendations (scored)
    - best_decision (top recommendation)
    - forbidden products
    - unknown inputs (symptoms/conditions not in your DB)
    """
    conditions_medicales = conditions_medicales or []

    symptomes_norm = [_norm(s) for s in symptomes if _norm(s)]
    conditions_norm = [_norm(c) for c in conditions_medicales if _norm(c)]

    known_s = _known_symptomes()
    known_c = _known_conditions()

    unknown_symptomes = sorted({s for s in symptomes_norm if s not in known_s})
    unknown_conditions = sorted({c for c in conditions_norm if c not in known_c})

    # Only feed known values to the engine (optional but cleaner)
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
    matches: Set[Tuple[str, str]] = set()  # (produit, symptome)

    for f in facts:
        if isinstance(f, ProduitInterdit):
            forbidden.add(f["produit"])
        elif isinstance(f, Recommandation):
            matches.add((f["nom"], f["cible"]))

    # Safety: remove any match for forbidden products (should already be excluded by NOT(...))
    matches = {(p, s) for (p, s) in matches if p not in forbidden}

    # Aggregate per product => score = number of distinct matched symptoms
    by_product: Dict[str, Set[str]] = {}
    for p, s in matches:
        by_product.setdefault(p, set()).add(s)

    recommendations: List[Dict[str, Any]] = []
    for produit, covered in by_product.items():
        recommendations.append(
            {
                "produit": produit,
                "score": len(covered),
                "symptomes_couverts": sorted(covered),
            }
        )

    recommendations.sort(key=lambda x: (-x["score"], x["produit"].lower()))
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
