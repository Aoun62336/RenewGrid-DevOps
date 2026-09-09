"""
routers/auth.py — Authentication + profile management.
Includes: register, login, me, update-profile, refresh-token,
          logout, forgot-password, reset-password, change-password,
          upload-profile-image, delete-account (NEW).
"""
import shutil
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile, status, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest, LoginResponse, RefreshTokenRequest,
    RefreshTokenResponse, RegisterRequest, RegisterResponse, UserPublic,
    ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest
)
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

PROFILE_IMG_DIR = Path("uploads/profile_images")
PROFILE_IMG_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


class UpdateProfileIn(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    profile_image: Optional[str] = None


# ─── Register ─────────────────────────────────────────────────────────────────
@router.post("/register", response_model=RegisterResponse, status_code=201,
             summary="Register a new account")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return auth_service.register(db, payload)


# ─── Login ────────────────────────────────────────────────────────────────────
@router.post("/login", response_model=LoginResponse, summary="Authenticate and get tokens")
@limiter.limit("5/minute")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, payload)


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
    if payload.profile_image is not None:
        current_user.profile_image = payload.profile_image
    db.commit()
    db.refresh(current_user)
    return current_user


# ─── Refresh Token ────────────────────────────────────────────────────────────
@router.post("/refresh-token", response_model=RefreshTokenResponse,
             summary="Exchange refresh token for new access token")
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    return auth_service.refresh_access_token(db, payload.refresh_token)


# ─── Logout ─────────────────────────────────────────────────────────────
@router.post("/logout", status_code=200, summary="Logout (client-side invalidation)")
def logout(current_user: User = Depends(get_current_user)):
    return {"message": f"Goodbye, {current_user.full_name}! Logged out successfully."}


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
    current_user: User = Depends(get_current_user)
):
    return auth_service.change_password(db, current_user, payload)


# ─── NEW: POST /auth/upload-profile-image ────────────────────────────────────
@router.post("/upload-profile-image", response_model=UserPublic,
             summary="Upload a profile picture (multipart/form-data)")
async def upload_profile_image(
    file: UploadFile = File(..., description="Profile image file (JPEG, PNG, WebP, GIF)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate content type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: {sorted(ALLOWED_IMAGE_TYPES)}"
        )

    # Validate file size (max 5MB)
    MAX_SIZE = 5 * 1024 * 1024
    content = await file.read()
    if len(content) > MAX_SIZE:
        from fastapi import HTTPException
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 5MB.")
    
    # Reset file pointer after reading
    await file.seek(0)

    ext = Path(file.filename).suffix or ".jpg"
    filename = f"user_{current_user.id}_{uuid.uuid4().hex}{ext}"
    dest = PROFILE_IMG_DIR / filename

    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    image_url = f"/uploads/profile_images/{filename}"
    current_user.profile_image = image_url
    db.commit()
    db.refresh(current_user)

    return current_user
