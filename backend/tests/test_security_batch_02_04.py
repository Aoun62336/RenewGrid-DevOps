"""Focused security regressions for password-reset and pickup handoff.

Run within RenewGrid's venv. Uses a temporary SQLite database; no live account
or production database is accessed.
"""
from types import SimpleNamespace
from datetime import datetime, timezone

import pytest
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.database import Base
from app.models.user import User, UserRole
from app.models.waste import WasteUpload, WasteCategory
from app.models.core import PickupRequest, PickupStatus
from app.core.security import (create_access_token, decode_access_token,
                               hash_password, verify_password)
from app.schemas.auth import ResetPasswordRequest
from app.services.auth_service import auth_service
from app.services import pickup_service


@pytest.fixture
def db(tmp_path):
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path / 'security-test.sqlite3'}")
    Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def test_password_reset_is_purpose_bound_single_use(db):
    user = User(full_name="Owner", email="owner@example.test", password_hash=hash_password("OldPass123"), role=UserRole.USER)
    db.add(user)
    db.commit()
    db.refresh(user)

    tasks = BackgroundTasks()
    auth_service.forgot_password(db, user.email, tasks)
    assert len(tasks.tasks) == 1
    reset_token = tasks.tasks[0].kwargs["reset_token"]

    # A normal access token cannot reset passwords, and reset tokens cannot log in.
    with pytest.raises(HTTPException) as err:
        auth_service.reset_password(db, ResetPasswordRequest(token=create_access_token(user.id, "dummy-session-id"), new_password="NewPass456"))
    assert err.value.status_code == 400
    with pytest.raises(Exception):
        decode_access_token(reset_token)

    auth_service.reset_password(db, ResetPasswordRequest(token=reset_token, new_password="NewPass456"))
    db.refresh(user)
    assert verify_password("NewPass456", user.password_hash)

    with pytest.raises(HTTPException) as err:
        auth_service.reset_password(db, ResetPasswordRequest(token=reset_token, new_password="OtherPass789"))
    assert err.value.status_code == 400


def test_signed_qr_and_manual_code_require_assigned_collector(db, monkeypatch):
    owner = User(full_name="Owner", email="owner@example.test", password_hash="unused", role=UserRole.USER)
    collector = User(full_name="Collector", email="collector@example.test", password_hash="unused", role=UserRole.COLLECTOR)
    other = User(full_name="Other", email="other@example.test", password_hash="unused", role=UserRole.COLLECTOR)
    db.add_all([owner, collector, other])
    db.flush()
    waste = WasteUpload(user_id=owner.id, title="Old laptop", category=WasteCategory.LAPTOPS, estimated_weight=2.0)
    db.add(waste)
    db.flush()
    pickup = PickupRequest(user_id=owner.id, waste_upload_id=waste.id, collector_id=collector.id,
                           address="Private home address", status=PickupStatus.ASSIGNED)
    db.add(pickup)
    db.commit()
    db.refresh(pickup)

    scanned = []
    class FakeImage:
        def save(self, buf, format="PNG"):
            buf.write(b"FAKEPNG")
    def fake_make(payload):
        scanned.append(payload)
        return FakeImage()
    monkeypatch.setattr(pickup_service.qrcode, "make", fake_make)

    issued = pickup_service.generate_qr_credentials(db, owner, pickup.id)
    assert issued["manual_code"].startswith(f"RG-{pickup.id}-")
    assert "Private home address" not in scanned[0]
    assert scanned[0].startswith("RG1.")

    with pytest.raises(HTTPException):
        pickup_service.verify_qr(db, other, issued["manual_code"])
    with pytest.raises(HTTPException):
        pickup_service.verify_qr(db, collector, f"RG-{pickup.id}-000000000000")

    verified = pickup_service.verify_qr(db, collector, scanned[0])
    assert verified.status == PickupStatus.IN_PROGRESS
    with pytest.raises(HTTPException) as err:
        pickup_service.verify_qr(db, collector, scanned[0])
    assert err.value.status_code == 409


def test_signed_qr_expires_and_manual_code_changes_by_window(db, monkeypatch):
    owner = User(full_name="Owner", email="owner2@example.test", password_hash="unused", role=UserRole.USER)
    collector = User(full_name="Collector", email="collector2@example.test", password_hash="unused", role=UserRole.COLLECTOR)
    db.add_all([owner,collector]);db.flush()
    waste = WasteUpload(user_id=owner.id,title="Phone",category=WasteCategory.MOBILE, estimated_weight=0.5)
    db.add(waste);db.flush()
    pickup = PickupRequest(user_id=owner.id,waste_upload_id=waste.id, collector_id=collector.id,
                           address="Private", status=PickupStatus.ASSIGNED)
    db.add(pickup);db.commit()
    now = 1_750_000_000
    monkeypatch.setattr(pickup_service.time, "time", lambda: now)
    code = pickup_service._manual_code(pickup.id, collector.id, now // pickup_service._QR_WINDOW_SECONDS)
    monkeypatch.setattr(pickup_service.time, "time", lambda: now + 2 * pickup_service._QR_WINDOW_SECONDS)
    with pytest.raises(HTTPException) as err:
        pickup_service.verify_qr(db, collector, code)
    assert err.value.status_code == 400
