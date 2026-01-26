# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **expert system for health and wellness product recommendations** that matches patient symptoms with products from a JSON catalogue while respecting medical contraindications and drug interactions. The system uses a simplified, direct matching approach for core functionality, with Experta available for advanced safety rule enforcement.

## Running the System

```bash
# Run the product recommendation system with test scenarios
python app.py
```

The system will execute 6 predefined test scenarios and display recommendations for each user profile.

## Architecture

### Three-Layer Design

The codebase follows a clean separation of concerns across three modules:

1. **database.py** - Data layer (loaded from JSON files)
        - Loads all product sheets from the `data/` folder at import time.
        - Public exports:
            - `CATALOGUE_COMPLET`: dict of categories → list of product sheets (each sheet is a dict loaded from JSON)
            - `CATALOGUE_PRODUITS` / `CONTRE_INDICATIONS`: flattened helper lists used by `service.py`
            - `CATEGORIES` / `CONDITIONS`: optional “meta” JSON from `data/categories` and `data/conditions`
        - Category mapping (keeps the same high-level idea while using `data/`):
            - `data/supplements` → `complement_alimentaire`
            - `data/other` → `sport_et_pratique`
            - `data/diets` → `regime_alimentaire`
        - Safety data is embedded per product under `safety.interactions`, `safety.pregnancy_lactation`, and `safety.precautions`.

2. **logic.py** - Core matching & inference engine
    - **Three key functions** (reusable everywhere):
      - `extract_health_conditions_from_supplements()`: Extracts all `health_condition_or_goal` from supplements database into a structured dict
      - `normalize_health_condition(condition: str)`: Normalizes conditions (e.g., "Santé du sommeil" → "sommeil")
      - `match_symptoms_with_products(symptoms: List[str])`: Matches patient symptoms against product conditions, returns scored recommendations
    
    - **Fact classes** (Experta - for future advanced safety rules):
      - `Produit`, `ContreIndication`, `BesoinClient`, `ConditionClient`, `ProduitInterdit`, `Recommandation`
    - `MoteurRecommandation`: Legacy inference engine (can still be used for complex safety validation in future)

3. **app.py** - User interface layer
    - `lancer_diagnostic(nom_user, symptomes, conditions_medicales)`: Main diagnostic function using `match_symptoms_with_products()`
    - `afficher_details_produit(nom_produit)`: Displays product details (description, dosage, interactions)
    - Contains 6 test scenarios

4. **test_suite.py** - Automated tests (unittest)
    - Unit tests: verifies data loading and extraction
    - Integration tests: verifies matching accuracy and filtering

### Inference Flow

```
Patient Symptoms (e.g., ["Sommeil", "Fatigue"])
    ↓
match_symptoms_with_products(symptoms)
    ↓
    ├─ extract_health_conditions_from_supplements()
    │  └─ Returns: {"Alpha-Lactalbumin": ["Santé du sommeil"], ...}
    │
    └─ For each symptom:
       ├─ normalize_health_condition(symptom)  → "sommeil"
       └─ Compare against normalized product conditions
    ↓
Return: {"Alpha-Lactalbumin": {"matched_symptoms": ["sommeil"], "score": 1}, ...}
    ↓
Display: Sorted by score (highest first)
```

### Key Design Patterns

- **Direct Matching Approach**: Simple, transparent symptom-to-product matching without heavy inference
- **Normalization Layer**: All conditions normalized consistently (removes stop words like "santé", "de", "du")
- **Scoring System**: Products scored by number of matched symptoms for relevance ranking
- **Reusable Functions**: Core extraction/normalization functions importable for use elsewhere
- **Safety-Ready**: Experta engine still available for contraindication/interaction checks (future enhancement)

## Python Compatibility

The system requires **Python 3.10+** and includes a compatibility patch in logic.py:

```python
import collections
import collections.abc
if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping
```

This patch redirects deprecated `collections.Mapping` (removed in Python 3.10) to `collections.abc.Mapping`.

## Core Functions Reference

### `extract_health_conditions_from_supplements()`
Extracts all health conditions from the supplement database.
```python
from logic import extract_health_conditions_from_supplements

conditions = extract_health_conditions_from_supplements()
# Returns: {"Alpha-Lactalbumin": ["Santé du sommeil"], "5-HTP": ["Dépression", "Sommeil"], ...}
```

### `normalize_health_condition(condition: str)`
Normalizes a health condition string.
```python
from logic import normalize_health_condition

normalized = normalize_health_condition("Santé du sommeil")
# Returns: "sommeil"
```

### `match_symptoms_with_products(symptoms: List[str])`
Matches patient symptoms with products.
```python
from logic import match_symptoms_with_products

recommendations = match_symptoms_with_products(["Sommeil", "Stress"])
# Returns:
# {
#   "Alpha-Lactalbumin": {
#       "matched_symptoms": ["sommeil"],
#       "raw_conditions": ["Santé du sommeil"],
#       "score": 1
#   },
#   "5-HTP": {
#       "matched_symptoms": ["sommeil", "stress"],
#       "raw_conditions": ["Anxiété", "Sommeil"],
#       "score": 2
#   }
# }
```

## Extending the System

### Adding New Products

Add a new JSON file under one of these folders:
- `data/supplements` (→ `complement_alimentaire`)
- `data/other` (→ `sport_et_pratique`)
- `data/diets` (→ `regime_alimentaire`)

Each product sheet should include (at minimum):
```json
{
    "name": "Product Name",
    "description": "...",
    "dosage": "...",
    "database": [
        {"health_condition_or_goal": "Dépression"},
        {"health_condition_or_goal": "Sommeil"}
    ],
    "safety": {
        "pregnancy_lactation": [],
        "interactions": [],
        "precautions": []
    }
}
```

### Adding New Test Scenarios

Edit `app.py` - Add calls to `lancer_diagnostic()`:
```python
lancer_diagnostic("User Name",
                  symptomes=['symptom1', 'symptom2'],
                  conditions_medicales=['condition1'])
```

To run automated tests:
```bash
python -m unittest -q
```

## Important Implementation Notes

- **No modification needed when adding products**: New products are automatically loaded and matched
- **Normalization is consistent**: All condition matching uses the same normalization function
- **Scoring is automatic**: Products are ranked by number of symptom matches
- **Reusable components**: Core functions can be imported and used in other modules
- **Future safety integration**: Experta engine can be enhanced to validate contraindications before display

## Documentation

- `Explication/EXPLICATION.md`: Detailed French documentation
- `Explication/RESULTATS_EXECUTION.md`: Execution results and examples
- `code progress.md`: Development progress and architectural decisions
