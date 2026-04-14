"""database.py

Objectif:
- Utiliser automatiquement les donnÃ©es JSON dans le dossier `data/`.
- Garder la mÃªme structure publique que le code existant attend:
  - `CATALOGUE_COMPLET`: dict[str, list[dict]]
  - (compat) `CATALOGUE_PRODUITS` et `CONTRE_INDICATIONS` pour `service.py`

Le moteur Experta (`logic.py`) itÃ¨re sur `CATALOGUE_COMPLET` et lit:
- `sheet['name']`
- `sheet['database'][*]['health_condition_or_goal']`
- `sheet['safety']` (pregnancy_lactation, interactions, precautions)

Les JSON de `data/` (supplements/other/diets) suivent dÃ©jÃ  ce schÃ©ma.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


_ROOT = Path(__file__).resolve().parent
_DATA_DIR = _ROOT / "data"


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_folder_json(folder: Path) -> List[Dict[str, Any]]:
    if not folder.exists() or not folder.is_dir():
        return []

    items: List[Dict[str, Any]] = []
    for p in sorted(folder.glob("*.json"), key=lambda x: x.name.lower()):
        try:
            items.append(_read_json(p))
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON invalide: {p}") from e
    return items


def _build_catalogue_from_data(data_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Construit un catalogue compatible avec le code existant.

Mapping (garde l'idÃ©e des catÃ©gories actuelles):
- data/supplements -> complement_alimentaire (recommendation)
- data/other       -> sport_et_pratique (practice)
- data/diets       -> regime_alimentaire (practice)

Note: `data/conditions` et `data/categories` sont chargÃ©s sÃ©parÃ©ment (voir plus bas),
car ce ne sont pas des "produits" au sens du moteur de recommandations.
"""

    # Map folder -> (category_key, category_type)
    mapping: List[Tuple[str, str, str]] = [
        ("supplements", "complement_alimentaire", "recommendation"),
        ("other", "sport_et_pratique", "practice"),
        ("diets", "regime_alimentaire", "practice"),
    ]

    catalogue: Dict[str, List[Dict[str, Any]]] = {}
    for folder_name, category_key, category_type in mapping:
        items = _load_folder_json(data_dir / folder_name)
        # Add category_type to each item
        for item in items:
            item["category_type"] = category_type
        catalogue[category_key] = items
    return catalogue


def _is_risky_pregnancy_text(text: str) -> bool:
    t = (text or "").strip().lower()
    risky_keywords = (
        "éviter",
        "eviter",
        "déconseill",
        "deconseill",
        "limiter",
        "éviction",
        "eviction",
        "ã©viter",
        "dã©conseill",
    )
    return any(k in t for k in risky_keywords)


def _extract_rules(catalogue: Dict[str, List[Dict[str, Any]]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Construit des listes "plates" pour le service layer.

CATALOGUE_PRODUITS: [{produit, cible}]
CONTRE_INDICATIONS: [{produit, condition}]
"""

    produits: List[Dict[str, Any]] = []
    contres: List[Dict[str, Any]] = []

    for _category, sheets in catalogue.items():
        for sheet in sheets:
            product_name = (sheet.get("name") or "").strip()
            if not product_name:
                continue

            # A) Indications (symptÃ´mes/cibles)
            for entry in sheet.get("database", []) or []:
                target = (entry.get("health_condition_or_goal") or "").strip().lower()
                if target:
                    produits.append({"produit": product_name, "cible": target})

            # B) SÃ©curitÃ© (contre-indications)
            safety = sheet.get("safety") or {}

            # grossesse / allaitement
            for pl in safety.get("pregnancy_lactation", []) or []:
                condition_text = (pl.get("condition") or "").strip()
                safety_info = (pl.get("safety_information") or "").strip()
                combined = f"{condition_text} {safety_info}"
                combined_l = combined.lower()

                if "grossesse" in combined_l and _is_risky_pregnancy_text(combined):
                    contres.append({"produit": product_name, "condition": "grossesse"})
                if "allait" in combined_l and _is_risky_pregnancy_text(combined):
                    contres.append({"produit": product_name, "condition": "allaitement"})

            # interactions mÃ©dicamenteuses
            for inter in safety.get("interactions", []) or []:
                agent = (inter.get("agent") or "").strip().lower()
                if agent:
                    contres.append({"produit": product_name, "condition": agent})

            # prÃ©cautions
            for prec in safety.get("precautions", []) or []:
                pop = (prec.get("population_condition") or "").strip().lower()
                if pop:
                    contres.append({"produit": product_name, "condition": pop})

    return produits, contres


# --- Chargement principal (utilisÃ© par logic.py / app.py) ---

CATALOGUE_COMPLET: Dict[str, List[Dict[str, Any]]] = _build_catalogue_from_data(_DATA_DIR)


# --- DonnÃ©es "meta" (optionnel) ---

CATEGORIES: List[Dict[str, Any]] = _load_folder_json(_DATA_DIR / "categories")
CONDITIONS: List[Dict[str, Any]] = _load_folder_json(_DATA_DIR / "conditions")


# --- CompatibilitÃ© service.py ---

CATALOGUE_PRODUITS, CONTRE_INDICATIONS = _extract_rules(CATALOGUE_COMPLET)


# --- Helper functions to get category type ---

def get_product_category_type(product_name: str) -> str:
    """Returns 'recommendation' or 'practice' for a given product name, or None if not found."""
    product_name_norm = (product_name or "").strip().lower()
    for _category, items in CATALOGUE_COMPLET.items():
        for item in items:
            if (item.get("name") or "").strip().lower() == product_name_norm:
                return item.get("category_type", "recommendation")
    return None


CATEGORY_TYPE_LABELS = {
    "recommendation": "Recommandations",
    "practice": "Pratiques pour de meilleurs résultats",
}
