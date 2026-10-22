"""Regression tests for pickup authorization and secure media."""
import os
from datetime import datetime, timezone
from io import BytesIO
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from PIL import Image
from starlette.datastructures import Headers
from fastapi import UploadFile

os.environ.setdefault(
    "DATABASE_URL",
    "sqlite+pysqlite:///./renewgrid-test.sqlite3",
)
os.environ.setdefault(
    "SECRET_KEY",
    "test-secret-for-isolated-security-tests",
)
os.environ.setdefault(
    "REFRESH_SECRET_KEY",
    "test-refresh-secret-for-isolated-tests",
)

from app.models.user import UserRole
from app.models.core import PickupStatus
from app.repositories.pickup_repository import pickup_repo
from app.services.pickup_service import (
    get_pickup_by_id,
    track_pickup,
)
from app.core.upload_security import prepare_image
from app.core.media_security import (
    media_url,
    verify_media_token,
    MEDIA_TTL_SECONDS,
)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _make_user(id_, role):
    """Build a minimal user SimpleNamespace."""
    return SimpleNamespace(id=id_, role=role)


def _make_pickup(
    id_,
    user_id,
    collector_id=None,
    recycler_id=None,
    status=PickupStatus.PENDING,
):
    """Build a minimal pickup SimpleNamespace."""
    return SimpleNamespace(
        id=id_,
        user_id=user_id,
        collector_id=collector_id,
        recycler_id=recycler_id,
        status=status,
        status_history=[],
    )


def _png_upload_file(size_bytes: int = 1024) -> UploadFile:
    """Create a valid in-memory PNG UploadFile."""
    buf = BytesIO()
    img = Image.new("RGB", (10, 10), color=(100, 149, 237))
    img.save(buf, format="PNG")
    buf.seek(0)

    return UploadFile(
        filename="test.png",
        file=buf,
        headers=Headers({"content-type": "image/png"}),
    )


# ─── Fix 05: Pickup authorization ─────────────────────────────────────────────

class TestPickupAuthorization:
    """get_pickup_by_id must enforce role-based access."""

    def _patch_repo(self, monkeypatch, pickup):
        monkeypatch.setattr(pickup_repo, "get_by_id", lambda db, id_: pickup)

    def test_owner_can_access_own_pickup(self, monkeypatch):
        pickup = _make_pickup(1, user_id=10)
        self._patch_repo(monkeypatch, pickup)
        user = _make_user(10, UserRole.USER)
        result = get_pickup_by_id(db=None, current_user=user, pickup_id=1)
        assert result is pickup

    def test_admin_can_access_any_pickup(self, monkeypatch):
        pickup = _make_pickup(2, user_id=99)
        self._patch_repo(monkeypatch, pickup)
        admin = _make_user(1, UserRole.ADMIN)
        result = get_pickup_by_id(db=None, current_user=admin, pickup_id=2)
        assert result is pickup

    def test_assigned_collector_can_access_pickup(self, monkeypatch):
        pickup = _make_pickup(3, user_id=10, collector_id=20)
        self._patch_repo(monkeypatch, pickup)
        collector = _make_user(20, UserRole.COLLECTOR)
        result = get_pickup_by_id(db=None, current_user=collector, pickup_id=3)
        assert result is pickup

    def test_unassigned_collector_gets_404(self, monkeypatch):
        pickup = _make_pickup(4, user_id=10, collector_id=20)
        self._patch_repo(monkeypatch, pickup)
        other_collector = _make_user(99, UserRole.COLLECTOR)
        with pytest.raises(HTTPException) as exc_info:
            get_pickup_by_id(db=None, current_user=other_collector, pickup_id=4)
        assert exc_info.value.status_code == 404

    def test_assigned_recycler_can_access_pickup(self, monkeypatch):
        pickup = _make_pickup(5, user_id=10, recycler_id=30)
        self._patch_repo(monkeypatch, pickup)
        recycler = _make_user(30, UserRole.RECYCLER)
        result = get_pickup_by_id(db=None, current_user=recycler, pickup_id=5)
        assert result is pickup

    def test_unassigned_recycler_gets_404(self, monkeypatch):
        pickup = _make_pickup(6, user_id=10, recycler_id=30)
        self._patch_repo(monkeypatch, pickup)
        other_recycler = _make_user(99, UserRole.RECYCLER)
        with pytest.raises(HTTPException) as exc_info:
            get_pickup_by_id(db=None, current_user=other_recycler, pickup_id=6)
        assert exc_info.value.status_code == 404

    def test_missing_pickup_returns_404(self, monkeypatch):
        monkeypatch.setattr(pickup_repo, "get_by_id", lambda db, id_: None)
        user = _make_user(1, UserRole.USER)
        with pytest.raises(HTTPException) as exc_info:
            get_pickup_by_id(db=None, current_user=user, pickup_id=999)
        assert exc_info.value.status_code == 404

    def test_track_pickup_enforces_same_authorization(self, monkeypatch):
        """track_pickup must re-use _get_authorized_pickup."""
        pickup = _make_pickup(7, user_id=10, collector_id=20)
        monkeypatch.setattr(pickup_repo, "get_by_id", lambda db, id_: pickup)
        bad_collector = _make_user(55, UserRole.COLLECTOR)
        with pytest.raises(HTTPException) as exc_info:
            track_pickup(db=None, current_user=bad_collector, pickup_id=7)
        assert exc_info.value.status_code == 404


# ─── Fix 06: Upload security ───────────────────────────────────────────────────

class TestUploadSecurity:
    """prepare_image validates and normalizes uploads."""

    def test_valid_png_is_accepted(self):
        upload = _png_upload_file()
        result = prepare_image(upload)
        # Result must be valid PNG bytes.
        out = Image.open(BytesIO(result))
        assert out.format == "PNG"

    def test_invalid_content_type_rejected(self):
        buf = BytesIO(b"not-an-image")
        upload = UploadFile(
            filename="bad.exe",
            file=buf,
            headers=Headers({"content-type": "application/octet-stream"}),
        )
        with pytest.raises(HTTPException) as exc_info:
            prepare_image(upload)
        assert exc_info.value.status_code == 400

    def test_oversized_file_rejected(self):
        # Build a PNG that exceeds the 5 MB limit by padding.
        buf = BytesIO()
        img = Image.new("RGB", (10, 10))
        img.save(buf, format="PNG")
        # Pad to just over 5 MB.
        buf.write(b"\x00" * (5 * 1024 * 1024 + 1))
        buf.seek(0)
        upload = UploadFile(
            filename="big.png",
            file=buf,
            headers=Headers({"content-type": "image/png"}),
        )
        with pytest.raises(HTTPException) as exc_info:
            prepare_image(upload)
        assert exc_info.value.status_code == 413


# ─── Fix 06: Signed media URLs ────────────────────────────────────────────────

class TestMediaSecurity:
    """media_url issues tokens; verify_media_token enforces them."""

    def test_private_path_gets_signed_url(self):
        path = "/uploads/waste/abc123.png"
        result = media_url(path)
        assert result is not None
        assert "?token=" in result

    def test_proof_path_gets_signed_url(self):
        path = "/uploads/proofs/def456.png"
        result = media_url(path)
        assert result is not None
        assert "?token=" in result

    def test_profile_path_is_not_signed(self):
        path = "/uploads/profile_images/user1.png"
        result = media_url(path)
        # Profile images are public — returned as-is.
        assert result == path
        assert "token" not in (result or "")

    def test_valid_token_passes_verification(self):
        path = "/uploads/waste/abc123.png"
        signed = media_url(path)
        token = signed.split("?token=")[1]
        # Should not raise.
        verify_media_token(path, token)

    def test_wrong_path_token_rejected(self):
        path_a = "/uploads/waste/abc123.png"
        path_b = "/uploads/waste/other999.png"
        signed = media_url(path_a)
        token = signed.split("?token=")[1]
        with pytest.raises(HTTPException) as exc_info:
            verify_media_token(path_b, token)
        assert exc_info.value.status_code == 403

    def test_missing_token_rejected(self):
        path = "/uploads/waste/abc123.png"
        with pytest.raises(HTTPException) as exc_info:
            verify_media_token(path, None)
        assert exc_info.value.status_code == 403

    def test_tampered_token_rejected(self):
        path = "/uploads/waste/abc123.png"
        with pytest.raises(HTTPException) as exc_info:
            verify_media_token(path, "tampered.invalid.token")
        assert exc_info.value.status_code == 403

    def test_none_path_returns_none(self):
        assert media_url(None) is None

    def test_invalid_path_returns_none(self):
        assert media_url("/etc/passwd") is None
        assert media_url("/uploads/../secret") is None
