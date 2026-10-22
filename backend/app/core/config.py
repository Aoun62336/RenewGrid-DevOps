"""
core/config.py — Application configuration
Reads all settings from the .env file via Pydantic BaseSettings.
"""
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── App ───────────────────────────────────────────────────────────────
    PROJECT_NAME: str = "RenewGrid"

    # ── Database ──────────────────────────────────────────────────────────
    DATABASE_URL: str

    # ── JWT ───────────────────────────────────────────────────────────────
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Email / SMTP ──────────────────────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""          # set in .env
    SMTP_PASS: str = ""          # set in .env (use Gmail App Password)

    # ── Frontend ──────────────────────────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:5173"

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Parsed from ALLOWED_ORIGINS in .env (comma-separated string).
    ALLOWED_ORIGINS: str | List[str] = ["http://localhost:5173", "http://localhost:5174"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: object) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v  # already a list (e.g. when set programmatically in tests)

    # ── Session Cookie ────────────────────────────────────────────────────────
    # Local HTTP development only. Require True behind production HTTPS.
    COOKIE_SECURE: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"         # ignore unknown keys in .env



# Singleton instance imported across the app
settings = Settings()
