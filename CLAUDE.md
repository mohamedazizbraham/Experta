# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **expert system using Experta** (Python rule engine) that recommends health and wellness products from a JSON-style catalogue based on user symptoms while respecting medical contraindications and drug interactions. The engine filters unsafe options first, then surfaces safe, personalized recommendations.

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

2. **logic.py** - Inference engine (core system)
    - Fact classes: `Produit`, `ContreIndication`, `BesoinClient`, `ConditionClient`, `ProduitInterdit`, `Recommandation`
    - `initial_loading()`: Scans `CATALOGUE_COMPLET` to yield `Produit` facts for each `health_condition_or_goal`, and `ContreIndication` facts for risky pregnancy/allaitement cases and for every listed interaction agent
    - `MoteurRecommandation` (KnowledgeEngine) rules:
      - **Rule 1 (Safety)**: `detecter_danger()` - Marks products as forbidden when the client has a matching contraindication or interaction
      - **Rule 2 (Recommendation)**: `generer_recommandation()` - Recommends products matching symptoms that are not forbidden

3. **app.py** - User interface layer
    - `lancer_diagnostic(nom_user, symptomes, conditions_medicales)`: Main diagnostic function; injects user symptoms/conditions as facts, runs the engine, and prints results
    - `afficher_details_produit(nom_produit)`: Looks up the full catalogue entry to show description, dosage, and interaction warnings
    - Contains 6 test scenarios (executed only when running `python app.py`, not on import)

4. **test_suite.py** - Automated tests (unittest)
    - Unit tests: verifies that `data/` categories are loaded and facts are generated
    - Integration/regression tests: verifies correct targets (“cibles”), correct category source, and safety filtering (pregnancy + interactions)

### Inference Flow

```
User Input (symptoms + medical conditions)
    ↓
Declare BesoinClient facts (symptoms)
Declare ConditionClient facts (medical conditions)
    ↓
Engine loads CATALOGUE_COMPLET (symptom coverage + safety)
    ↓
Rule 1 executes: Identify forbidden products (interactions + pregnancy/lactation)
    ↓
Rule 2 executes: Generate recommendations (matching + safe products only)
    ↓
Output: Filtered list of safe, relevant product recommendations
```

### Key Design Patterns

- **Safety-First Architecture**: Contraindication and interaction checking (Rule 1) executes before recommendations (Rule 2)
- **Multi-Target Products**: Products can target multiple symptoms via multiple `database` entries per item
- **Negative Filtering**: Uses `NOT(ProduitInterdit(produit=MATCH.p))` in Rule 2 to ensure forbidden products are never recommended
- **Fact-Based Inference**: All data (products, contraindications/interactions, client needs) are represented as Facts that trigger rules

## Python Compatibility

The system requires **Python 3.10+** and includes a compatibility patch in logic.py:

```python
import collections
import collections.abc
if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping
```

This patch is necessary because Experta uses the deprecated `collections.Mapping` (removed in Python 3.10). The patch redirects it to `collections.abc.Mapping`.

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
        "pregnancy_lactation": [{"condition": "Éviter pendant la grossesse", "safety_information": "..."}],
        "interactions": [{"agent": "warfarin"}],
        "precautions": [{"population_condition": "hypertension", "details": "..."}]
    }
}
```

Products can target multiple symptoms via several `database` entries and carry multiple interaction agents.

### Adding New Contraindications

Add pregnancy/lactation precautions or `interactions` agents under each product's `safety` block; `initial_loading()` will convert them into `ContreIndication` facts automatically.

### Adding New Test Scenarios

Edit `app.py` - Add calls to `lancer_diagnostic()`:
```python
lancer_diagnostic("User Name",
                  symptomes=['symptom1', 'symptom2'],
                  conditions_medicales=['condition1'])
```
Six scenarios are provided as examples; you can append new ones at the bottom of `app.py`.

To run automated tests:
```bash
python -m unittest -q
```

## Important Implementation Notes

- **No modification needed to logic.py when adding products/contraindications**: The inference engine automatically processes new entries from `CATALOGUE_COMPLET`
- **Rule execution is automatic**: Experta handles rule matching and firing order based on declared Facts
- **Duplicate recommendations are filtered**: `app.py` uses a set (`deja_affiche`) to avoid printing the same product twice when it matches multiple needs
- **Test scenarios cover safety cases**: See `Explication/RESULTATS_EXECUTION.md` for execution results showing the system correctly filters contraindicated or interacting products

## Documentation

- `Explication/EXPLICATION.md`: Detailed French documentation explaining system architecture, data flow, and component roles
- `Explication/RESULTATS_EXECUTION.md`: Execution results for the predefined test scenarios with safety verification
