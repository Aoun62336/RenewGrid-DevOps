"""Regression tests for public registration security."""
import os
from types import SimpleNamespace
from unittest.mock import Mock

# Safe test defaults. No live database is accessed.
os.environ.setdefault(
    "DATABASE_URL",
    "sqlite+pysqlite:///./renewgrid-registration-test.sqlite3",
)
os.environ.setdefault(
    "SECRET_KEY",
    "registration-test-access-secret",
)
os.environ.setdefault(
    "REFRESH_SECRET_KEY",
    "registration-test-refresh-secret",
)

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.core.deps import get_current_user
from app.core.security import verify_password
from app.db.database import get_db
from app.models.user import UserRole
from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.services import admin_service
from app.services.auth_service import auth_repo

VALID_REGISTRATION = {
    "full_name": "Sample User",
    "email": "sample@example.com",
    "password": "SecurePass123!",
}


@pytest.fixture
def registration_api(monkeypatch):
    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(admin_router, prefix="/admin")

    # Override database access with an isolated test object.
    fake_db = object()
    app.dependency_overrides[get_db] = lambda: fake_db

    get_by_email = Mock(return_value=None)
    create_user = Mock(return_value=SimpleNamespace(id=42))

    monkeypatch.setattr(
        auth_repo, "get_by_email", get_by_email
    )
    monkeypatch.setattr(
        auth_repo, "create", create_user
    )

    with TestClient(app) as client:
        yield app, client, get_by_email, create_user
