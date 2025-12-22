# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **expert system using Experta** (Python fuzzy logic library) that recommends health and wellness products based on user symptoms while respecting medical contraindications. The system uses rule-based inference to filter dangerous products and generate safe, personalized recommendations.

## Running the System

```bash
# Run the product recommendation system with test scenarios
python app.py
```

The system will execute 4 predefined test scenarios and display recommendations for each user profile.

## Architecture

### Three-Layer Design

The codebase follows a clean separation of concerns across three modules:

1. **database.py** - Static data layer
   - `CATALOGUE_PRODUITS`: 20 health products with their target symptoms (products can target multiple symptoms)
   - `CONTRE_INDICATIONS`: Safety rules linking products to incompatible medical conditions

2. **logic.py** - Inference engine (core system)
   - Fact classes: `Produit`, `ContreIndication`, `BesoinClient`, `ConditionClient`, `ProduitInterdit`, `Recommandation`
   - `MoteurRecommandation` (KnowledgeEngine): Contains two critical rules:
     - **Rule 1 (Safety)**: `detecter_danger()` - Marks products as forbidden when client has contraindicated conditions
     - **Rule 2 (Recommendation)**: `generer_recommandation()` - Recommends products matching symptoms that are NOT forbidden
   - `chargement_initial()`: Loads catalog and contraindications into the knowledge base

3. **app.py** - User interface layer
   - `lancer_diagnostic(nom_user, symptomes, conditions_medicales)`: Main diagnostic function
   - Contains 4 test scenarios demonstrating different medical profiles

### Inference Flow

```
User Input (symptoms + medical conditions)
    ↓
Declare BesoinClient facts (symptoms)
Declare ConditionClient facts (medical conditions)
    ↓
Engine loads CATALOGUE_PRODUITS and CONTRE_INDICATIONS
    ↓
Rule 1 executes: Identify forbidden products (safety filter)
    ↓
Rule 2 executes: Generate recommendations (matching + safe products only)
    ↓
Output: Filtered list of safe, relevant product recommendations
```

### Key Design Patterns

- **Safety-First Architecture**: Contraindication checking (Rule 1) executes before recommendations (Rule 2)
- **Multi-Target Products**: Products in the catalog can target multiple symptoms (e.g., "Magnesium Bisglycinate" targets both stress and fatigue)
- **Negative Filtering**: Uses `NOT(ProduitInterdit(produit=MATCH.p))` in Rule 2 to ensure forbidden products are never recommended
- **Fact-Based Inference**: All data (products, contraindications, client needs) are represented as Facts that trigger rules

## Python Compatibility

The system requires **Python 3.10+** and includes a compatibility patch in logic.py:

```python
import collections.abc
if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping
```

This patch is necessary because Experta uses the deprecated `collections.Mapping` (removed in Python 3.10). The patch redirects it to `collections.abc.Mapping`.

## Extending the System

### Adding New Products

Edit `database.py` - `CATALOGUE_PRODUITS`:
```python
{"nom": "Product Name", "cible": "symptom"}
```

Products can appear multiple times with different targets to support multi-symptom coverage.

### Adding New Contraindications

Edit `database.py` - `CONTRE_INDICATIONS`:
```python
{"produit": "Product Name", "condition": "medical_condition"}
```

### Adding New Test Scenarios

Edit `app.py` - Add calls to `lancer_diagnostic()`:
```python
lancer_diagnostic("User Name",
                  symptomes=['symptom1', 'symptom2'],
                  conditions_medicales=['condition1'])
```

## Important Implementation Notes

- **No modification needed to logic.py when adding products/contraindications**: The inference engine automatically processes new entries from database.py
- **Rule execution is automatic**: Experta handles rule matching and firing order based on declared Facts
- **Duplicate recommendations are filtered**: app.py uses a set (`recommandations_uniques`) to eliminate duplicate product-target pairs in output
- **All test scenarios are validated**: See `Explication/RESULTATS_EXECUTION.md` for validation results showing the system correctly filters contraindicated products

## Documentation

- `Explication/EXPLICATION.md`: Detailed French documentation explaining system architecture, data flow, and component roles
- `Explication/RESULTATS_EXECUTION.md`: Execution results for all 4 test scenarios with safety verification
