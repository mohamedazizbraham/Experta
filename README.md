# Experta

Real backend for the `AJA_ptut` frontend. This project exposes a FastAPI API, stores users and recommendations in MongoDB, and runs the rule-based recommendation engine used by the app.

## What This Project Does

- Auth API for signup / login
- User profile storage
- Recommendation generation from goals, symptoms, and medical constraints
- Recommendation history and intake tracking
- Encyclopedie data for supplements

For the client demo, this is the backend that must be started before `AJA_ptut`.

## Client Run Guide

### Prerequisites

- Python 3.10+
- MongoDB running locally on `mongodb://127.0.0.1:27017`
- The sibling frontend project in `d:\ptut\AJA_ptut`

### 1. Configure environment variables

Create `.env` from the example file:

```powershell
cd d:\ptut\Experta
Copy-Item .env.example .env
```

Default values expected by the app:

```env
MONGODB_URI=mongodb://127.0.0.1:27017
MONGODB_DB=aja
JWT_SECRET=replace-with-a-long-random-secret
JWT_EXPIRES_MINUTES=10080
```

Change `JWT_SECRET` before handing the project to a real client environment.

### 2. Install dependencies

```powershell
cd d:\ptut\Experta
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Start the API

```powershell
cd d:\ptut\Experta
.venv\Scripts\Activate.ps1
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:

- `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

## Start The Frontend That Uses This Backend

In a second terminal:

```powershell
cd d:\ptut\AJA_ptut
Copy-Item .env.example .env
npm install
npm run web
```

Then open `http://localhost:8082`.

## How `Experta` And `AJA_ptut` Work Together

`AJA_ptut` is only the interface. `Experta` is the source of truth for live data.

Request flow:

1. `AJA_ptut` sends auth requests to `/auth/signup` and `/auth/login`.
2. The onboarding form saves profile data through `PUT /users/me/profile`.
3. The recommendations screen calls `GET /decide/me`.
4. `Experta` converts the saved profile into goals, symptoms, and medical conditions.
5. The rule engine runs through `service.py` / `logic.py`.
6. The selected recommendation is saved in MongoDB and returned to the frontend.
7. Tracking screens then read and write recommendation intake data through the API.
8. Encyclopedie screens read supplement content from backend endpoints.

If this backend is down, the frontend UI can still load, but the app cannot authenticate, generate recommendations, or save tracking data.

## Main Runtime Files

- `api.py`: FastAPI application used by the frontend
- `mongo.py`: MongoDB connection and env settings
- `security.py`: password hashing and JWT handling
- `service.py`: recommendation orchestration
- `logic.py`: Experta rule engine
- `database.py` + `data/`: knowledge base used by the engine

## Important Note About `app.py`

`app.py` is not the normal client runtime anymore. It is a standalone script for manual rule-engine scenarios.

For the real app and for the client demo, run:

```powershell
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

## Useful Commands

```powershell
# Run the backend
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Run backend tests
python -m unittest test_suite.py

# Quick Mongo connectivity check
python test_mongo.py
```
