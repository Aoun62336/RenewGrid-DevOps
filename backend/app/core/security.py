"""
core/security.py — JWT token creation, verification, and password hashing.
All cryptographic operations live here — nothing else touches tokens or hashes.
"""
import os
import hashlib
import hmac
import secrets

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


def create_access_token(
    subject: Any,
    session_id: str,
) -> str:
    """Create a short-lived JWT bound to a revocable session.

    Claims:
      sub  — user_id (str)
      sid  — auth_sessions.id linking the JWT to a revocable record
      exp  — expiry timestamp
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {
            "sub": str(subject),
            "sid": session_id,
            "exp": expire,
        },
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
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


# Password-reset credentials are distinct from normal login credentials.
_RESET_AUDIENCE = "renewgrid-password-reset"
_RESET_ISSUER = "renewgrid"


def _reset_signing_key() -> str:
    return hmac.new(settings.SECRET_KEY.encode(), b"renewgrid/password-reset/v1", hashlib.sha256).hexdigest()


def password_reset_fingerprint(password_hash: str) -> str:
    return hmac.new(_reset_signing_key().encode(), password_hash.encode(), hashlib.sha256).hexdigest()


def create_password_reset_token(user_id: int, password_hash: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(user_id),
            "purpose": "password_reset",
            "pwd": password_reset_fingerprint(password_hash),
            "jti": secrets.token_urlsafe(24),
            "aud": _RESET_AUDIENCE,
            "iss": _RESET_ISSUER,
            "iat": now,
            "exp": now + timedelta(minutes=30),
        },
        _reset_signing_key(),
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_password_reset_token(token: str) -> dict:
    payload = jwt.decode(
        token,
        _reset_signing_key(),
        algorithms=[settings.JWT_ALGORITHM],
        audience=_RESET_AUDIENCE,
        issuer=_RESET_ISSUER,
    )
    if payload.get("purpose") != "password_reset" or not payload.get("jti"):
        raise JWTError("Invalid password-reset token purpose")
    return payload
