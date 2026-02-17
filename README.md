# Experta - Expert System for Holistic Health Recommendations

A rule-based expert system using Experta (Python knowledge engine library) that recommends integrated health interventions based on user symptoms while respecting medical contraindications and safety constraints.

## Features

- **Rule-based inference engine** for intelligent product and intervention recommendations
- **Holistic approach** supporting multiple intervention types: Supplements, Herbs, and Wellness Practices
- **Safety-first architecture** with automated contraindication filtering based on:
  - Pregnancy and lactation precautions
  - Drug-product interactions
  - Medical conditions
- **Multi-symptom targeting** with mixed recommendations (e.g., Magnesium + Yoga for stress)
- **Pre-configured test scenarios** demonstrating complex medical profiles
- **Rich metadata** per product including efficacy evidence levels and interaction data

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

1. **database.py** - Static data layer (Knowledge Base)
   - `CATALOGUE_COMPLET`: Comprehensive catalogue organized by intervention categories:
     - **Compléments** (Nutritional supplements)
     - **Herbes Naturelles** (Herbal remedies)
     - **Pratiques Sportives** (Wellness practices)
   - Each intervention contains:
     - Basic metadata: name, description, dosage/practice guidelines
     - `database`: Health conditions/goals the intervention addresses
     - `safety`: Contraindication rules (pregnancy, lactation, drug interactions)

2. **logic.py** - Inference engine (Knowledge Engine)
   - **Fact classes**:
     - `Produit`: Represents an intervention and its target conditions
     - `ContreIndication`: Represents safety restrictions (pregnancy, drug interactions)
     - `BesoinClient`: User's symptoms or health goals
     - `ConditionClient`: User's medical status (Pregnancy, current medications, etc.)
     - `ProduitInterdit`: Internal marker for contraindicated interventions
     - `Recommandation`: Final validated recommendation
   
   - **`chargement_initial()`**: Smart loader that:
     - Scans `CATALOGUE_COMPLET` recursively through categories
     - Converts products into `Produit` facts per target condition
     - Extracts `ContreIndication` facts from pregnancy/lactation warnings and drug interactions
   
   - **`MoteurRecommandation` (KnowledgeEngine) rules**:
     - **Rule: `detecter_danger()`** - Safety filtering: marks products as forbidden when the client has matching contraindications
     - **Rule: `generer_recommandation()`** - Intelligent recommendation: suggests safe products matching user symptoms across all intervention categories

3. **app.py** - User interface layer
   - `lancer_diagnostic(nom_user, symptomes, conditions_medicales)`: Main diagnostic function
     - Injects user symptoms/conditions as facts
     - Executes the inference engine
     - Returns filtered recommendations
   
   - `afficher_details_produit(nom_produit)`: Product information display
     - Retrieves full catalogue entry
     - Shows description, dosage/practice details
     - Displays interaction warnings and safety notes
   
   - **Test scenarios**: Demonstrates system behavior with complex medical profiles
     - Scenarios covering depression, pregnancy, contraceptive interactions, insomnia, hypertension, and anticoagulants

### Sample Output

The system executes predefined test scenarios showing how the inference engine:
1. Loads all interventions and their contraindications
2. Analyzes user medical profile (symptoms + conditions)
3. Filters dangerous products (marks as forbidden)
4. Recommends safe alternatives matching the user's needs
5. Displays detailed information for each recommendation

## Extending the System

### Adding New Interventions

Edit `database.py` - Add entries to `CATALOGUE_COMPLET`:

```python
"Compléments": [
    {
        "name": "Intervention Name",
        "description": "Detailed description",
        "dosage": "e.g., 200mg/jour or practice frequency",
        "database": [
            {"health_condition_or_goal": "stress"},
            {"health_condition_or_goal": "sommeil"}
        ],
        "safety": {
            "pregnancy_lactation": [
                {"condition": "Grossesse", "safety_information": "Avoid if..."}
            ],
            "interactions": [
                {"agent": "anticoagulants", "severity": "high"}
            ]
        }
    }
]
```

**Key points:**
- Add to appropriate category: "Compléments", "Herbes Naturelles", or "Pratiques Sportives"
- Multiple `database` entries allow targeting multiple conditions
- Safety rules are automatically converted to facts by `chargement_initial()`

### Adding New Contraindications

Update the `safety` block in any intervention:
- **Pregnancy/Lactation**: Add entries to `safety.pregnancy_lactation`
- **Drug Interactions**: Add entries to `safety.interactions` with agent names and severity levels
- Changes are automatically processed by the inference engine

### Adding New Test Scenarios

Edit `app.py` - Add calls to `lancer_diagnostic()` at the bottom:

```python
lancer_diagnostic("User Name",
                  symptomes=['stress', 'fatigue'],
                  conditions_medicales=['pregnancy'])
```

Scenarios demonstrate how the system handles different medical profiles and safety constraints.

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

The system includes a compatibility patch for Python 3.10+ because Experta uses the deprecated `collections.Mapping`. This patch is automatically handled in `logic.py`:

```python
import collections.abc
if not hasattr(collections, "Mapping"):
    collections.Mapping = collections.abc.Mapping
```

This ensures the system runs smoothly on modern Python versions.

## Technical Details

- **Framework**: Experta 1.9.4 (Python rule-based inference engine)
- **Python Version**: 3.10 or higher (required)
- **Architecture**: Fact-based knowledge representation with rule-driven inference
- **Safety Model**: Negative filtering (contraindicated interventions are excluded before recommendation generation)
- **Data Model**: Hierarchical catalogue with category-based organization

## Documentation

- **CLAUDE.md**: Guidance for AI assistants working with this codebase
- **FRONTEND_HANDOFF.md**: Backend files and API contract to share with frontend developers
- **code progress.md**: Development progress notes and architectural decisions
- **Explication/EXPLICATION.md**: Comprehensive French documentation explaining system architecture, data flow, and evolution
- **Explication/RESULTATS_EXECUTION.md**: Validation results and test execution outputs (French)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
