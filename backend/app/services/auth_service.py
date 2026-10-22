"""
services/auth_service.py — Business logic for the auth module.

Service methods:
  • validate input rules that span multiple layers (e.g. duplicate email)
  • hash passwords before passing them to the repository
  • generate and verify JWT tokens
  • never execute raw SQL — delegate everything to auth_repo
  • delete_account — soft-delete by setting is_active=False
"""
import hmac

from fastapi import BackgroundTasks, HTTPException, status
from jose import JWTError
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    create_password_reset_token,
    decode_password_reset_token,
    password_reset_fingerprint,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.repositories.auth_repository import auth_repo
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenResponse,
    RegisterRequest,
    RegisterResponse,
    UserPublic,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
)
from app.services.email_service import send_reset_email
from app.services.session_service import (
    issue_session,
    rotate_session,
    session_is_active,
    revoke_all_sessions,
)


class AuthService:

    # ── Register ──────────────────────────────────────────────────────────
    def register(self, db: Session, payload: RegisterRequest) -> RegisterResponse:
        """
        Register a public user account.
        Public registration is restricted to UserRole.USER.
        Privileged accounts are provisioned through admin-only endpoints.
        """
        existing = auth_repo.get_by_email(db, email=payload.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

        user = auth_repo.create(
            db,
            full_name=payload.full_name,
            email=payload.email,
            phone_number=payload.phone_number,
            password_hash=hash_password(payload.password),
            role=UserRole.USER,
        )

        return RegisterResponse(
            message="User registered successfully",
            user_id=user.id,
        )

    # ── Login ─────────────────────────────────────────────────────────────
    def login(
        self,
        db: Session,
        payload: LoginRequest,
    ) -> tuple[LoginResponse, str]:
        """
        1. Look up the user by email.
        2. Verify the password hash.
        3. Check the account is active.
        4. Issue a session-bound access JWT + opaque refresh credential.
        Returns (LoginResponse, refresh_credential).
        """
        user = auth_repo.get_by_email(db, email=payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated. Contact support.",
            )

        session_id, refresh_credential = issue_session(db, user.id)
        db.commit()

        result = LoginResponse(
            access_token=create_access_token(user.id, session_id),
            user=UserPublic.model_validate(user),
        )
        return result, refresh_credential

    # ── Get Current User ──────────────────────────────────────────────────
    def get_current_user(
        self,
        db: Session,
        token: str,
    ) -> User:
        """
        Decode the bearer token, verify the embedded session is still active,
        and return the corresponding User object.
        Raises 401 on any invalid/expired/revoked token.
        """
        unauthorized = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            claims = decode_access_token(token)
            user_id = int(claims["sub"])
            session_id = claims["sid"]
        except (JWTError, KeyError, TypeError, ValueError):
            raise unauthorized

        user = auth_repo.get_by_id(db, user_id=user_id)
        if user is None or not user.is_active:
            raise unauthorized

        if not session_is_active(db, session_id, user.id):
            raise unauthorized

        return user

    # ── Refresh Token ─────────────────────────────────────────────────────
    def refresh_access_token(
        self,
        db: Session,
        credential: str,
    ) -> tuple[RefreshTokenResponse, str]:
        """
        Rotate the opaque refresh credential and issue a new access JWT.
        Returns (RefreshTokenResponse, new_refresh_credential).
        """
        session_id, user_id, replacement = rotate_session(db, credential)

        user = auth_repo.get_by_id(db, user_id=user_id)
        if user is None or not user.is_active:
            revoke_all_sessions(db, user_id)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account unavailable.",
            )
        db.commit()

        result = RefreshTokenResponse(
            access_token=create_access_token(user.id, session_id),
            user=UserPublic.model_validate(user),
        )
        return result, replacement

    # ── Password Management ───────────────────────────────────────────────
    def forgot_password(
        self,
        db: Session,
        email: str,
        background_tasks: BackgroundTasks,
    ) -> dict:
        """
        Generate a signed reset token and dispatch a password-reset email.

        - Always returns the same generic message to prevent user enumeration.
        - Email is sent via BackgroundTask (non-blocking).
        - Token is never included in the API response.
        """
        # Generic response — returned regardless of whether the user exists.
        _ok = {"message": "If an account with that email exists, a password reset link has been sent."}

        user = auth_repo.get_by_email(db, email=email)
        if not user or not user.is_active:
            return _ok

        reset_token = create_password_reset_token(user.id, user.password_hash)

        # Fire-and-forget: send email after response is returned.
        background_tasks.add_task(send_reset_email, to_email=user.email, reset_token=reset_token)

        return _ok

    def reset_password(self, db: Session, payload: ResetPasswordRequest) -> dict:
        """Consume a purpose-bound, expiring token exactly once.

        Optimistic compare-and-swap prevents concurrent replay even on multiple
        application replicas. A reset-token cannot authenticate as an access token.
        """
        invalid = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token.",
        )
        try:
            claims = decode_password_reset_token(payload.token)
            user_id = int(claims["sub"])
        except (JWTError, ValueError, KeyError, TypeError):
            raise invalid

        user = auth_repo.get_by_id(db, user_id=user_id)
        if not user or not user.is_active:
            raise invalid
        previous_hash = user.password_hash
        if not isinstance(claims.get("pwd"), str):
            raise invalid
        if not hmac.compare_digest(claims["pwd"], password_reset_fingerprint(previous_hash)):
            raise invalid

        new_hash = hash_password(payload.new_password)
        result = db.execute(
            update(User)
            .where(User.id == user_id, User.password_hash == previous_hash, User.is_active.is_(True))
            .values(password_hash=new_hash)
        )
        if result.rowcount != 1:
            db.rollback()
            raise invalid

        # Revoke all existing sessions so old access JWTs are rejected.
        revoke_all_sessions(db, user_id)
        db.commit()
        return {"message": "Password has been reset successfully."}

    def change_password(
        self,
        db: Session,
        current_user: User,
        payload: ChangePasswordRequest,
    ) -> dict:
        """Change the password for the currently authenticated user."""
        if not verify_password(payload.old_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password.",
            )

        current_user.password_hash = hash_password(payload.new_password)
        revoke_all_sessions(db, current_user.id)
        db.commit()
        return {"message": "Password changed successfully."}

    # ── Delete Account ────────────────────────────────────────────────
    def delete_account(self, db: Session, current_user: User) -> dict:
        """
        Soft-delete the authenticated user:
        • Set is_active = False (blocks future logins)
        • Revoke all active sessions
        """
        current_user.is_active = False
        revoke_all_sessions(db, current_user.id)
        db.commit()
        return {"message": "Account has been deactivated successfully."}


# ── Module-level singleton ────────────────────────────────────────────────────
auth_service = AuthService()
