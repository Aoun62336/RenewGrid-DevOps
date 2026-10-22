"""Signed access to private RenewGrid media."""
import hashlib
import hmac
import re
import time

from fastapi import HTTPException
from jose import JWTError, jwt

from app.core.config import settings

PRIVATE_FOLDERS = {"waste", "proofs"}
MEDIA_TTL_SECONDS = 900  # 15 minutes

MEDIA_PATH_PATTERN = re.compile(
    r"^/uploads/(waste|proofs|profile_images)/"
    r"([A-Za-z0-9][A-Za-z0-9_.-]{0,180})$"
)


def _media_signing_key() -> str:
    return hmac.new(
        settings.SECRET_KEY.encode(),
        b"renewgrid/media-access/v1",
        hashlib.sha256,
    ).hexdigest()


def media_url(path: str | None) -> str | None:
    """Issue a temporary signed URL for media in an authorized API response.

    - Public folders (profile_images): returns the path unchanged.
    - Private folders (waste, proofs): returns a path with a short-lived token.
    - Invalid or missing paths: returns None.
    """
    if not path:
        return None

    match = MEDIA_PATH_PATTERN.fullmatch(path)
    if not match:
        return None

    folder = match.group(1)

    if folder not in PRIVATE_FOLDERS:
        # Avatar images are public — no token needed.
        return path

    # Issue a signed JWT valid for MEDIA_TTL_SECONDS.
    now = int(time.time())
    payload = {
        "sub": path,
        "purpose": "media_access",
        "iat": now,
        "exp": now + MEDIA_TTL_SECONDS,
    }
    token = jwt.encode(payload, _media_signing_key(), algorithm=settings.JWT_ALGORITHM)
    return f"{path}?token={token}"


def verify_media_token(path: str, token: str | None) -> None:
    """Validate a signed media token.  Raises 403 on any failure."""
    invalid = HTTPException(
        status_code=403,
        detail="Missing or invalid media access token.",
    )

    if token is None:
        raise invalid

    try:
        claims = jwt.decode(
            token,
            _media_signing_key(),
            algorithms=[settings.JWT_ALGORITHM],
        )
        if claims.get("purpose") != "media_access":
            raise invalid
        if claims.get("sub") != path:
            raise invalid
    except JWTError:
        raise invalid
