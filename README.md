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

1. **database.py** - Contains static data:
   - Product catalog (20 health products with target symptoms)
   - Contraindications (safety rules for medical conditions)

2. **logic.py** - Inference engine with two critical rules:
   - **Rule 1 (Safety)**: Identifies and marks forbidden products based on medical conditions
   - **Rule 2 (Recommendation)**: Recommends safe products matching user symptoms

3. **app.py** - User interface with test scenarios

### Sample Output

The system runs 4 test scenarios:
- **Student**: Stress + Fatigue (no medical restrictions)
- **Pregnant Woman**: Fatigue + Sleep + Stress (pregnancy restrictions)
- **Senior with Hypertension**: Joint + Fatigue (hypertension restrictions)
- **Cardiac Patient**: Immunity + Joint (anticoagulant restrictions)

Each scenario demonstrates how the system filters dangerous products and recommends safe alternatives.

## Extending the System

### Adding New Products

Edit `database.py` - `CATALOGUE_PRODUITS`:
```python
{"nom": "New Product", "cible": "target_symptom"}
```

### Adding New Contraindications

Edit `database.py` - `CONTRE_INDICATIONS`:
```python
{"produit": "Product Name", "condition": "medical_condition"}
```

### Adding New Test Scenarios

Edit `app.py`:
```python
lancer_diagnostic("Profile Name",
                  symptomes=['symptom1', 'symptom2'],
                  conditions_medicales=['condition1'])
```

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
