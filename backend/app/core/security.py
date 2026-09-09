"""
core/security.py — JWT token creation, verification, and password hashing.
All cryptographic operations live here — nothing else touches tokens or hashes.
"""
import os

# Suppress passlib's bcrypt version detection warning (bcrypt 4.x compat fix)
os.environ.setdefault("PASSLIB_SUPPRESS_BCRYPT_VERSION_WARNING", "1")

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt as _bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# ── Password Hashing ──────────────────────────────────────────────────────────
# Use bcrypt directly — passlib 1.7.4 is incompatible with bcrypt 4.x


def hash_password(plain_password: str) -> str:
    """Return the bcrypt hash of a plain-text password."""
    hashed = _bcrypt.hashpw(plain_password.encode("utf-8"), _bcrypt.gensalt(rounds=12))
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against the stored bcrypt hash."""
    try:
        return _bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


# ── JWT Helpers ───────────────────────────────────────────────────────────────
def _create_token(subject: Any, secret: str, expire_delta: timedelta) -> str:
    """
    Internal helper — builds a signed JWT with `sub` and `exp` claims.
    """
    expire = datetime.now(timezone.utc) + expire_delta
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, secret, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: Any) -> str:
    """
    Create a short-lived JWT access token.
    Lifetime: ACCESS_TOKEN_EXPIRE_MINUTES (default 30 min).
    """
    return _create_token(
        subject,
        secret=settings.SECRET_KEY,
        expire_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(subject: Any) -> str:
    """
    Create a long-lived JWT refresh token (signed with a **different** secret).
    Lifetime: REFRESH_TOKEN_EXPIRE_DAYS (default 7 days).
    """
    return _create_token(
        subject,
        secret=settings.REFRESH_SECRET_KEY,
        expire_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_access_token(token: str) -> dict:
    """
    Decode & verify an access token.
    Raises JWTError if the token is expired or tampered with.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def decode_refresh_token(token: str) -> dict:
    """
    Decode & verify a refresh token.
    Raises JWTError if the token is expired or tampered with.
    """
    return jwt.decode(
        token, settings.REFRESH_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
