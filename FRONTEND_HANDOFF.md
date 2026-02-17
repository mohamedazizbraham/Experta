# Frontend Handoff

This document lists the backend files the frontend developer needs, what each file does, and the API endpoints/contracts that must be consumed.

## Required Files (Frontend Integration)

### `api.py`
Main API contract used by frontend apps.

What it provides:
- Auth models and endpoints:
  - `SignupRequest`, `LoginRequest`, `TokenResponse`
  - `POST /auth/signup`
  - `POST /auth/login`
- User/profile models and endpoints:
  - `UserResponse`, `PersonalInfoUpdate`, `MedicalInfoUpdate`, `ProfileUpdate`
  - `GET /users/me`
  - `PUT /users/me/profile`
- Recommendation models and endpoints:
  - `DecideRequest`, `RecommendationResponse`
  - `POST /decide`
  - `GET /decide/me`
  - `GET /users/me/recommendations`
  - `GET /users/me/recommendations/{recommendation_id}`
- Recommendation persistence:
  - `GET /decide/me` computes a recommendation and saves it in MongoDB (`recommendations` collection).

### `mongo.py`
MongoDB configuration and dependency wiring for the API.

What it provides:
- Required environment variables:
  - `MONGODB_URI`
  - `JWT_SECRET`
- Optional/default variables:
  - `MONGODB_DB` (default `aja`)
  - `JWT_EXPIRES_MINUTES`
- DB dependency function used by API routes:
  - `get_db()`

### `security.py`
Authentication and token behavior used by frontend login/session flows.

What it provides:
- Password server-side hashing and verification:
  - `hash_password(...)`
  - `verify_password(...)`
- JWT creation and decoding:
  - `create_access_token(...)`
  - `decode_access_token(...)`
- Token format:
  - User ID is stored in JWT claim `sub`.

### `service.py`
Recommendation service contract consumed by `/decide` and `/decide/me`.

Output fields (important for frontend rendering):
- `best_decision`
- `recommendations`
- `forbidden_products`
- `unknown_symptomes`
- `unknown_conditions`

### `requirements.txt`
Backend dependencies needed to run the API locally.

## Needed Only If Frontend Developer Also Runs Full Recommendation Engine

### `logic.py`
Rule engine and matching logic.

### `database.py`
Loads and transforms JSON knowledge data used by the engine.

### `data/`
Knowledge base JSON files (required for real recommendation results).

## Optional But Useful

### `README.md`
General setup and run instructions.

### `.env.example`
Template for required environment variables:

```env
MONGODB_URI=mongodb://127.0.0.1:27017
MONGODB_DB=aja
JWT_SECRET=replace-with-a-long-random-secret
JWT_EXPIRES_MINUTES=10080
```

## Frontend Integration Notes

- Protected endpoints require header:
  - `Authorization: Bearer <access_token>`
- Typical app flow:
  1. `POST /auth/signup` or `POST /auth/login`
  2. Save `access_token`
  3. `GET /users/me` to fetch user profile
  4. `PUT /users/me/profile` to update profile/goals/medical info
  5. `GET /decide/me` to compute and persist recommendation
  6. `GET /users/me/recommendations` to display recommendation history
