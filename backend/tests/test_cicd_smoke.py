
"""Focused CI smoke tests for the RenewGrid FastAPI application."""

import os

os.environ.setdefault(
    "DATABASE_URL",
    "sqlite:///./cicd-smoke.sqlite3",
)
os.environ.setdefault(
    "SECRET_KEY",
    "temporary-ci-smoke-key",
)
os.environ.setdefault(
    "REFRESH_SECRET_KEY",
    "temporary-ci-smoke-refresh-key",
)

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_application_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_public_roles_endpoint():
    response = client.get("/roles")

    assert response.status_code == 200

    expected_roles = {
        "user",
        "collector",
        "recycler",
        "admin",
    }

    actual_roles = set(response.json()["roles"])

    assert expected_roles.issubset(actual_roles)


def test_registration_rejects_admin_role():
    response = client.post(
        "/auth/register",
        json={
            "full_name": "CI Example",
            "email": "ci-example@example.com",
            "password": "ExamplePassword123!",
            "role": "admin",
        },
    )

    assert response.status_code == 422
