"""
routers/auth.py — Authentication + profile management.
Includes: register, login, me, update-profile, refresh-token,
          logout, forgot-password, reset-password, change-password,
          upload-profile-image, delete-account.
"""
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Request, Response, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.limiter import limiter
from app.core.deps import get_current_user, get_db
from app.core.upload_security import (
    prepare_image,
    save_prepared_image,
    delete_uploaded_path,
)
from app.models.user import User
from app.schemas.auth import (
    LoginRequest, LoginResponse, RefreshTokenResponse,
    RegisterRequest, RegisterResponse, UserPublic,
    ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest,
)
from app.services.auth_service import auth_service
from app.services.session_service import revoke_session

router = APIRouter(prefix="/auth", tags=["Authentication"])

AUTH_COOKIE_NAME = "renewgrid_refresh"


def _validate_cookie_request(request: Request) -> None:
    """Reject cross-site browser requests to cookie-based auth routes."""
    origin = request.headers.get("origin")
    fetch_site = request.headers.get("sec-fetch-site")

    allowed_origins = {
        settings.FRONTEND_URL.rstrip("/"),
        *(value.rstrip("/") for value in settings.ALLOWED_ORIGINS),
        str(request.base_url).rstrip("/"),
    }

    if origin and origin.rstrip("/") not in allowed_origins:
        raise HTTPException(403, "Untrusted request origin.")
    if fetch_site == "cross-site":
        raise HTTPException(403, "Cross-site request denied.")
    if request.headers.get("x-requested-with") != "XMLHttpRequest":
        raise HTTPException(403, "Missing CSRF request header.")


def _set_refresh_cookie(response: Response, credential: str) -> None:
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=credential,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        path="/auth",
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="strict",
    )


class UpdateProfileIn(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None


# ─── Register ─────────────────────────────────────────────────────────────────
@router.post("/register", response_model=RegisterResponse, status_code=201,
             summary="Register a new account")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return auth_service.register(db, payload)


# ─── Login ────────────────────────────────────────────────────────────────────
@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate and create a revocable session",
)
@limiter.limit("5/minute")
def login(
    request: Request,
    response: Response,
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    _validate_cookie_request(request)
    result, credential = auth_service.login(db, payload)
    _set_refresh_cookie(response, credential)
    return result


# ─── Me ───────────────────────────────────────────────────────────────────────
@router.get("/me", response_model=UserPublic, summary="Get my profile")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# ─── Update Profile ───────────────────────────────────────────────────────────
@router.put("/update-profile", response_model=UserPublic, summary="Update editable profile fields")
def update_profile(
    payload: UpdateProfileIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.phone_number is not None:
        current_user.phone_number = payload.phone_number
    if payload.address is not None:
        current_user.address = payload.address
    db.commit()
    db.refresh(current_user)
    return current_user


# ─── Refresh Token ────────────────────────────────────────────────────────────
@router.post(
    "/refresh-token",
    response_model=RefreshTokenResponse,
    summary="Rotate the refresh credential",
)
@limiter.limit("20/minute")
def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    _validate_cookie_request(request)
    credential = request.cookies.get(AUTH_COOKIE_NAME)
    if not credential:
        raise HTTPException(
            status_code=401,
            detail="Refresh session not found.",
        )
    result, replacement = auth_service.refresh_access_token(db, credential)
    _set_refresh_cookie(response, replacement)
    return result


# ─── Logout ─────────────────────────────────────────────────────────────
@router.post(
    "/logout",
    status_code=200,
    summary="Revoke the current session",
)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    _validate_cookie_request(request)
    credential = request.cookies.get(AUTH_COOKIE_NAME)
    revoke_session(db, credential)
    _clear_refresh_cookie(response)
    return {"message": "Logged out successfully."}


# ─── Delete Account ─────────────────────────────────────────────────────
@router.delete("/delete-account", status_code=200, summary="Soft-delete the authenticated user's account")
def delete_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return auth_service.delete_account(db, current_user)


# ─── Password Management ──────────────────────────────────────────────────────
@router.post("/forgot-password", summary="Request a password reset link")
@limiter.limit("5/minute")
def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    return auth_service.forgot_password(db, payload.email, background_tasks)


@router.post("/reset-password", summary="Reset password using a token")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    return auth_service.reset_password(db, payload)


@router.post("/change-password", summary="Change current account password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return auth_service.change_password(db, current_user, payload)


# ─── Upload Profile Image ────────────────────────────────────────────────────
@router.post(
    "/upload-profile-image",
    response_model=UserPublic,
    summary="Upload a validated profile image",
)
def upload_profile_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prepared = prepare_image(file)
    previous_path = current_user.profile_image
    new_path = save_prepared_image(prepared, folder="profile_images")
    try:
        current_user.profile_image = new_path
        db.commit()
        db.refresh(current_user)
    except Exception:
        db.rollback()
        delete_uploaded_path(new_path)
        raise
    if previous_path and previous_path != new_path:
        delete_uploaded_path(previous_path)
    return current_user
