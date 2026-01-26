from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from mongo import get_settings

ALGORITHM = "HS256"


def _prehash(password: str) -> bytes:
    # évite les problèmes bcrypt (72 bytes) + stable
    return hashlib.sha256(password.encode("utf-8")).digest()


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(_prehash(password), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(_prehash(password), password_hash.encode("utf-8"))
    except Exception:
        return False


def create_access_token(user_id: str) -> str:
    s = get_settings()
    exp = datetime.now(timezone.utc) + timedelta(minutes=s.JWT_EXPIRES_MINUTES)
    payload = {"sub": user_id, "exp": exp}
    return jwt.encode(payload, s.JWT_SECRET, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    s = get_settings()
    return jwt.decode(token, s.JWT_SECRET, algorithms=[ALGORITHM])
