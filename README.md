# Experta - Expert System for Product Recommendation

A rule-based expert system using Experta (Python fuzzy logic library) that recommends health and wellness products based on user symptoms while respecting medical contraindications.

## Features

- Rule-based inference engine for intelligent product recommendations
- Safety-first architecture that filters products based on medical contraindications
- Support for multi-symptom targeting
- Pre-configured test scenarios demonstrating different medical profiles
- 20 health products covering Energy, Immunity, Stress, Sleep, Digestion, and Joint health

## Prerequisites

### Without Docker
- Python 3.10 or higher
- pip

### With Docker
- Docker
- Docker Compose (optional, but recommended)

## Installation & Running

### Option 1: Running Without Docker

1. **Clone the repository** (if not already done):
```bash
git clone <repository-url>
cd Experta
```

2. **Create a virtual environment** (REQUIRED - do not install packages globally):
```bash
python3 -m venv venv
```

3. **Activate the virtual environment**:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

5. **Run the system**:
```bash
python app.py
```

6. **Deactivate the virtual environment when done**:
```bash
deactivate
```

### Option 2: Running With Docker

#### Using Docker directly:

1. **Build the Docker image**:
```bash
docker build -t experta-system .
```

2. **Run the container**:
```bash
docker run --rm experta-system
```

#### Using Docker Compose (recommended):

1. **Build and run with a single command**:
```bash
docker-compose up
```

2. **Rebuild after code changes**:
```bash
docker-compose up --build
```

3. **Run in detached mode** (background):
```bash
docker-compose up -d
```

4. **View logs**:
```bash
docker-compose logs -f
```

5. **Stop the service**:
```bash
docker-compose down
```

## How It Works

The system uses a three-layer architecture:

1. **database.py** - Static data layer
   - `CATALOGUE_COMPLET`: Full catalogue of products (name, description, dosage, `database` entries for efficacy per condition, and `safety` blocks for pregnancy/lactation and drug interactions)
   - Safety data is embedded per product under `safety.interactions` and `safety.pregnancy_lactation`

2. **logic.py** - Inference engine (core system)
   - Fact classes: `Produit`, `ContreIndication`, `BesoinClient`, `ConditionClient`, `ProduitInterdit`, `Recommandation`
   - `chargement_initial()`: Scans `CATALOGUE_COMPLET` to yield `Produit` facts for each `health_condition_or_goal`, and `ContreIndication` facts for risky pregnancy/allaitement cases and for every listed interaction agent
   - `MoteurRecommandation` (KnowledgeEngine) rules:
     - **Rule 1 (Safety)**: `detecter_danger()` - Marks products as forbidden when the client has a matching contraindication or interaction
     - **Rule 2 (Recommendation)**: `generer_recommandation()` - Recommends products matching symptoms that are not forbidden

3. **app.py** - User interface layer
   - `lancer_diagnostic(nom_user, symptomes, conditions_medicales)`: Main diagnostic function; injects user symptoms/conditions as facts, runs the engine, and prints results
   - `afficher_details_produit(nom_produit)`: Looks up the full catalogue entry to show description, dosage, and interaction warnings
   - Contains 6 test scenarios covering depression, contraceptives, pregnancy, insomnia, hypertension, and anticoagulants

### Sample Output

The system runs 6 predefined test scenarios demonstrating different medical profiles and safety constraints. Each scenario shows how the system filters dangerous products based on contraindications and drug interactions, then recommends safe alternatives that match the user's symptoms.

## Extending the System

### Adding New Products

Edit `database.py` - `CATALOGUE_COMPLET` entries:
```python
{
    "name": "Product Name",
    "description": "Short blurb",
    "dosage": "e.g., 200mg/jour",
    "database": [
        {"health_condition_or_goal": "dépression"},
        {"health_condition_or_goal": "sommeil"}
    ],
    "safety": {
        "pregnancy_lactation": [{"condition": "Grossesse", "safety_information": "Éviter"}],
        "interactions": [{"agent": "anticoagulants"}]
    }
}
```

Products can target multiple symptoms via several `database` entries and carry multiple interaction agents.

### Adding New Contraindications

Add pregnancy/lactation precautions or `interactions` agents under each product's `safety` block; `chargement_initial()` will convert them into `ContreIndication` facts automatically.

### Adding New Test Scenarios

Edit `app.py` - Add calls to `lancer_diagnostic()`:
```python
lancer_diagnostic("User Name",
                  symptomes=['symptom1', 'symptom2'],
                  conditions_medicales=['condition1'])
```

Six scenarios are provided as examples; you can append new ones at the bottom of `app.py`.

## Project Structure

```
Experta/
├── app.py                          # Main application with test scenarios
├── database.py                     # Product catalog and contraindications
├── logic.py                        # Inference engine (Experta rules)
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── docker-compose.yml              # Docker Compose orchestration
├── README.md                       # This file
├── CLAUDE.md                       # Claude Code guidance
└── Explication/
    ├── EXPLICATION.md              # Detailed system documentation (French)
    └── RESULTATS_EXECUTION.md      # Test execution results (French)
```

## Python 3.10+ Compatibility

The system includes a compatibility patch for Python 3.10+ because Experta uses the deprecated `collections.Mapping`. This is automatically handled in `logic.py`.

## Technical Details

- **Framework**: Experta 1.9.4 (Python expert system framework)
- **Python Version**: 3.10+
- **Architecture**: Rule-based inference with fact-based knowledge representation
- **Safety Model**: Negative filtering (contraindicated products are excluded before recommendation)

## Documentation

- `CLAUDE.md`: Guidance for AI assistants working with this codebase
- `Explication/EXPLICATION.md`: Detailed French documentation explaining architecture and data flow
- `Explication/RESULTATS_EXECUTION.md`: Validation results for all test scenarios

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
