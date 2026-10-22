"""Server-side refresh-session management for RenewGrid."""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import AuthSession


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _new_credential() -> str:
    return secrets.token_urlsafe(48)


def issue_session(
    db: Session,
    user_id: int,
) -> tuple[str, str]:
    """Create a new session record.  Caller must commit the transaction.

    Returns:
        (session_id, refresh_credential) — the credential is the raw
        opaque token that will be stored in the HttpOnly cookie.
        The database stores only its SHA-256 digest.
    """
    credential = _new_credential()
    session = AuthSession(
        user_id=user_id,
        token_digest=_digest(credential),
        expires_at=_now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(session)
    # Flush so session.id is populated without committing.
    db.flush()
    return session.id, credential


def rotate_session(
    db: Session,
    credential: str,
) -> tuple[str, int, str]:
    """Validate the incoming credential and issue a replacement.

    Caller must commit.

    Returns:
        (new_session_id, user_id, new_credential)

    Raises:
        HTTPException 401 if the credential is unknown, expired, or revoked.
    """
    invalid = HTTPException(
        status_code=401,
        detail="Refresh session not found or expired.",
    )
    digest = _digest(credential)
    session = (
        db.query(AuthSession)
        .filter(AuthSession.token_digest == digest)
        .first()
    )
    if session is None:
        raise invalid
    if session.revoked_at is not None:
        raise invalid
    if _aware(session.expires_at) < _now():
        raise invalid

    user_id = session.user_id

    # Revoke the consumed credential immediately.
    session.revoked_at = _now()

    # Issue a replacement credential.
    new_credential = _new_credential()
    new_session = AuthSession(
        user_id=user_id,
        token_digest=_digest(new_credential),
        expires_at=_now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_session)
    db.flush()
    return new_session.id, user_id, new_credential


def session_is_active(
    db: Session,
    session_id: str,
    user_id: int,
) -> bool:
    """Return True when the session is valid and belongs to the user."""
    session = db.get(AuthSession, session_id)
    if session is None:
        return False
    if session.user_id != user_id:
        return False
    if session.revoked_at is not None:
        return False
    if _aware(session.expires_at) < _now():
        return False
    return True


def revoke_session(
    db: Session,
    credential: str | None,
) -> None:
    """Revoke the session identified by credential.  Never raises."""
    if not credential:
        return
    try:
        digest = _digest(credential)
        session = (
            db.query(AuthSession)
            .filter(AuthSession.token_digest == digest)
            .first()
        )
        if session and session.revoked_at is None:
            session.revoked_at = _now()
            db.commit()
    except Exception:
        db.rollback()


def revoke_all_sessions(
    db: Session,
    user_id: int,
) -> None:
    """Revoke every active session for the given user.  Caller commits."""
    now = _now()
    (
        db.query(AuthSession)
        .filter(
            AuthSession.user_id == user_id,
            AuthSession.revoked_at.is_(None),
        )
        .update({"revoked_at": now}, synchronize_session=False)
    )
