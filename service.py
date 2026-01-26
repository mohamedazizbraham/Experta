from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

from database import CATALOGUE_PRODUITS, CONTRE_INDICATIONS
from logic import (
    MoteurRecommandation,
    BesoinClient,
    ConditionClient,
    Recommandation,
    ProduitInterdit,
    normalize_health_condition,
)


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
