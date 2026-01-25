"""database.py

Objectif:
- Utiliser automatiquement les données JSON dans le dossier `data/`.
- Garder la même structure publique que le code existant attend:
  - `CATALOGUE_COMPLET`: dict[str, list[dict]]
  - (compat) `CATALOGUE_PRODUITS` et `CONTRE_INDICATIONS` pour `service.py`

Le moteur Experta (`logic.py`) itère sur `CATALOGUE_COMPLET` et lit:
- `sheet['name']`
- `sheet['database'][*]['health_condition_or_goal']`
- `sheet['safety']` (pregnancy_lactation, interactions, precautions)

Les JSON de `data/` (supplements/other/diets) suivent déjà ce schéma.
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

Mapping (garde l'idée des catégories actuelles):
- data/supplements -> complement_alimentaire
- data/other       -> sport_et_pratique
- data/diets       -> regime_alimentaire

Note: `data/conditions` et `data/categories` sont chargés séparément (voir plus bas),
car ce ne sont pas des "produits" au sens du moteur de recommandations.
"""

    mapping: List[Tuple[str, str]] = [
        ("supplements", "complement_alimentaire"),
        ("other", "sport_et_pratique"),
        ("diets", "regime_alimentaire"),
    ]

    catalogue: Dict[str, List[Dict[str, Any]]] = {}
    for folder_name, category_key in mapping:
        catalogue[category_key] = _load_folder_json(data_dir / folder_name)
    return catalogue


def _is_risky_pregnancy_text(text: str) -> bool:
    t = (text or "").strip().lower()
    risky_keywords = ("éviter", "eviter", "déconseill", "deconseill", "limiter", "éviction", "eviction")
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

            # A) Indications (symptômes/cibles)
            for entry in sheet.get("database", []) or []:
                target = (entry.get("health_condition_or_goal") or "").strip().lower()
                if target:
                    produits.append({"produit": product_name, "cible": target})

            # B) Sécurité (contre-indications)
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

            # interactions médicamenteuses
            for inter in safety.get("interactions", []) or []:
                agent = (inter.get("agent") or "").strip().lower()
                if agent:
                    contres.append({"produit": product_name, "condition": agent})

            # précautions
            for prec in safety.get("precautions", []) or []:
                pop = (prec.get("population_condition") or "").strip().lower()
                if pop:
                    contres.append({"produit": product_name, "condition": pop})

    return produits, contres


# --- Chargement principal (utilisé par logic.py / app.py) ---

CATALOGUE_COMPLET: Dict[str, List[Dict[str, Any]]] = _build_catalogue_from_data(_DATA_DIR)


# --- Données "meta" (optionnel) ---

CATEGORIES: List[Dict[str, Any]] = _load_folder_json(_DATA_DIR / "categories")
CONDITIONS: List[Dict[str, Any]] = _load_folder_json(_DATA_DIR / "conditions")


# --- Compatibilité service.py ---

CATALOGUE_PRODUITS, CONTRE_INDICATIONS = _extract_rules(CATALOGUE_COMPLET)
