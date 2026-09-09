"""
services/auth_service.py — Business logic for the auth module.

Service methods:
  • validate input rules that span multiple layers (e.g. duplicate email)
  • hash passwords before passing them to the repository
  • generate and verify JWT tokens
  • never execute raw SQL — delegate everything to auth_repo
  • delete_account — soft-delete by setting is_active=False
"""
from fastapi import BackgroundTasks, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
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


class AuthService:

    # ── Register ──────────────────────────────────────────────────────────
    def register(self, db: Session, payload: RegisterRequest) -> RegisterResponse:
        """
        1. Ensure the email is not already taken.
        2. Hash the password.
        3. Persist the new user.
        4. Return a slim confirmation response.
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
            role=payload.role,
        )

        return RegisterResponse(
            message="User registered successfully",
            user_id=user.id,
        )

    # ── Login ─────────────────────────────────────────────────────────────
    def login(self, db: Session, payload: LoginRequest) -> LoginResponse:
        """
        1. Look up the user by email.
        2. Verify the password hash.
        3. Check the account is active.
        4. Issue access + refresh tokens.
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

        return LoginResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
            user=UserPublic.model_validate(user),
        )

    # ── Get Current User ──────────────────────────────────────────────────
    def get_current_user(self, db: Session, token: str) -> User:
        """
        Decode the bearer token and return the corresponding User object.
        Raises 401 on any invalid/expired token.
        """
        credentials_exc = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = decode_access_token(token)
            user_id: str | None = payload.get("sub")
            if user_id is None:
                raise credentials_exc
        except JWTError:
            raise credentials_exc

        user = auth_repo.get_by_id(db, user_id=int(user_id))
        if user is None or not user.is_active:
            raise credentials_exc
        return user

    # ── Refresh Token ─────────────────────────────────────────────────────
    def refresh_access_token(
        self, db: Session, refresh_token: str
    ) -> RefreshTokenResponse:
        """
        Validate the refresh token and issue a new short-lived access token.
        The refresh token itself is NOT rotated here — add rotation if needed.
        """
        credentials_exc = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )
        try:
            payload = decode_refresh_token(refresh_token)
            user_id: str | None = payload.get("sub")
            if user_id is None:
                raise credentials_exc
        except JWTError:
            raise credentials_exc

        user = auth_repo.get_by_id(db, user_id=int(user_id))
        if user is None or not user.is_active:
            raise credentials_exc

        return RefreshTokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id)
        )

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

        reset_token = create_access_token(user.id)

        # Fire-and-forget: send email after response is returned.
        background_tasks.add_task(send_reset_email, to_email=user.email, reset_token=reset_token)

        return _ok

    def reset_password(self, db: Session, payload: ResetPasswordRequest) -> dict:
        """
        Validate the reset token and update the user's password.
        """
        try:
            token_data = decode_access_token(payload.token)
            user_id = token_data.get("sub")
            if user_id is None:
                raise JWTError("Invalid token payload")
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token."
            )
            
        user = auth_repo.get_by_id(db, user_id=int(user_id))
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token or user."
            )
            
        user.password_hash = hash_password(payload.new_password)
        db.commit()
        return {"message": "Password has been reset successfully."}
        
    def change_password(self, db: Session, current_user: User, payload: ChangePasswordRequest) -> dict:
        """
        Change the password for the currently authenticated user.
        """
        if not verify_password(payload.old_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Incorrect current password."
            )
            
        current_user.password_hash = hash_password(payload.new_password)
        db.commit()
        return {"message": "Password changed successfully."}

    # ── Delete Account ────────────────────────────────────────────────
    def delete_account(self, db: Session, current_user: User) -> dict:
        """
        Soft-delete the authenticated user:
        • Set is_active = False (blocks future logins)
        • Clear the refresh_token field if the model has one
        """
        current_user.is_active = False
        # Clear refresh token if the column exists on the model
        if hasattr(current_user, 'refresh_token'):
            current_user.refresh_token = None
        db.commit()
        return {"message": "Account has been deactivated successfully."}



# ── Module-level singleton ────────────────────────────────────────────────────
auth_service = AuthService()
