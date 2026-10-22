"""
schemas/auth.py — Pydantic request/response schemas for the auth module.

Pydantic v2 is used here (FastAPI 0.100+ ships with Pydantic v2 by default).
All validators run before data ever reaches service/repository layers.
"""
import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.models.user import UserRole



# ─────────────────────────────────────────────────────────────────────────────
#  Register
# ─────────────────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    """Public registration payload. Accounts always receive the USER role."""
    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(
        ..., min_length=2, max_length=150, description="Full display name"
    )
    email: EmailStr = Field(
        ..., description="Valid e-mail address (must be unique)"
    )
    phone_number: Optional[str] = Field(
        None, description="10–15 digit phone number (optional)"
    )
    password: str = Field(
        ..., min_length=8, max_length=128, description="Minimum 8 characters"
    )

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        cleaned = re.sub(r"[\s\-\+\(\)]", "", v)
        if not re.fullmatch(r"\d{10,15}", cleaned):
            raise ValueError("Phone number must contain 10–15 digits.")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must include at least one digit.")
        return v


class RegisterResponse(BaseModel):
    """Slim success response returned after successful registration."""
    message: str
    user_id: int


# ─────────────────────────────────────────────────────────────────────────────
#  Login
# ─────────────────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    """Payload accepted by POST /auth/login."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserPublic(BaseModel):
    """Minimal user data returned to the client — never expose password_hash."""
    id: int
    full_name: str
    email: str
    role: UserRole
    is_active: bool
    is_available: bool = True
    created_at: datetime
    profile_image: Optional[str] = None

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    """Login response — only the short-lived access JWT + user info.
    The refresh credential travels in an HttpOnly cookie, not here."""
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


# ─────────────────────────────────────────────────────────────────────────────
#  Refresh Token
# ─────────────────────────────────────────────────────────────────────────────
class RefreshTokenResponse(BaseModel):
    """Refresh response — new access JWT + user info.
    The rotated refresh credential travels in an HttpOnly cookie."""
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


# ─────────────────────────────────────────────────────────────────────────────
#  Password Management
# ─────────────────────────────────────────────────────────────────────────────
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must include at least one digit.")
        return v


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must include at least one digit.")
        return v
