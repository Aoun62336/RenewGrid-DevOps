"""
services/pickup_service.py — Business logic for pickup requests.
"""
import io
import base64
import hashlib
import hmac
import re
import time
from datetime import datetime, timezone
from jose import JWTError, jwt
from sqlalchemy import update
from app.core.config import settings
import qrcode
from typing import List, Tuple, Dict, Any, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse

from app.models.user import User, UserRole
from app.models.core import PickupRequest, PickupStatus
from app.schemas.pickup import PickupCreate
from app.repositories.pickup_repository import pickup_repo
from app.repositories.waste_repository import waste_repo

def create_pickup(db: Session, current_user: User, body: PickupCreate) -> PickupRequest:
    waste = waste_repo.get_by_id(db, body.waste_id)
    if not waste or waste.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Waste upload not found or not yours.")

    pickup = pickup_repo.create(db, current_user.id, body.waste_id, body.address, body.pickup_date, body.notes)
    pickup_repo.add_history(db, pickup.id, PickupStatus.PENDING, current_user.id, "Pickup request created")
    db.commit()
    db.refresh(pickup)
    return pickup

def get_user_pickups(db: Session, current_user: User, page: int, page_size: int,
                     status=None, from_date=None, to_date=None):
    return pickup_repo.get_by_user_paginated(
        db, current_user.id, page, page_size,
        status=status, from_date=from_date, to_date=to_date,
    )


def list_reviews(db: Session, pickup_id: Optional[int]) -> List[Dict[str, Any]]:
    reviews = pickup_repo.get_reviews(db, pickup_id)
    return [
        {
            "id": r.id,
            "pickup_id": r.pickup_id,
            "user_name": r.user.full_name if r.user else "Unknown",
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.isoformat(),
        }
        for r in reviews
    ]

# QR credentials are short-lived, role-bound and never embed pickup addresses.
_QR_WINDOW_SECONDS = 600  # 10-minute display/verification window
_MANUAL_PATTERN = re.compile(r"^RG-(\d+)-(\d{12})$")


def _qr_signing_key() -> str:
    return hmac.new(settings.SECRET_KEY.encode(), b"renewgrid/pickup-qr/v1", hashlib.sha256).hexdigest()


def _manual_code(pickup_id: int, collector_id: int, window: int) -> str:
    message = f"manual|{pickup_id}|{collector_id}|{window}".encode()
    digest = hmac.new(_qr_signing_key().encode(), message, hashlib.sha256).digest()
    return f"RG-{pickup_id}-{int.from_bytes(digest[:8], 'big') % 10**12:012d}"


def _get_allowed_qr_pickup(db: Session, current_user: User, pickup_id: int) -> PickupRequest:
    pickup = pickup_repo.get_by_id(db, pickup_id)
    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found.")
    allowed = (pickup.user_id == current_user.id
               or current_user.role == UserRole.ADMIN
               or (current_user.role == UserRole.COLLECTOR and pickup.collector_id == current_user.id))
    if not allowed:
        raise HTTPException(status_code=403, detail="Access denied.")
    if pickup.status != PickupStatus.ASSIGNED or pickup.collector_id is None:
        raise HTTPException(status_code=409, detail="QR verification is available only for assigned pickups.")
    return pickup


def generate_qr_credentials(db: Session, current_user: User, pickup_id: int) -> Dict[str, Any]:
    pickup = _get_allowed_qr_pickup(db, current_user, pickup_id)
    now = int(time.time())
    window = now // _QR_WINDOW_SECONDS
    expires_at = (window + 1) * _QR_WINDOW_SECONDS
    payload = {
        "sub": str(pickup.id), "collector_id": pickup.collector_id,
        "purpose": "pickup_handoff", "aud": "renewgrid-collector",
        "iss": "renewgrid", "iat": now, "exp": expires_at,
    }
    encoded = jwt.encode(payload, _qr_signing_key(), algorithm=settings.JWT_ALGORITHM)
    image = qrcode.make("RG1." + encoded)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return {
        "pickup_id": pickup.id,
        "image_data_url": "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii"),
        "manual_code": _manual_code(pickup.id, pickup.collector_id, window),
        "expires_at": datetime.fromtimestamp(expires_at, tz=timezone.utc).isoformat(),
    }


def generate_qr(db: Session, current_user: User, pickup_id: int) -> StreamingResponse:
    """Compatibility image endpoint. New frontend uses credentials JSON endpoint."""
    credentials = generate_qr_credentials(db, current_user, pickup_id)
    image_bytes = base64.b64decode(credentials["image_data_url"].split(",", 1)[1])
    return StreamingResponse(io.BytesIO(image_bytes), media_type="image/png",
                             headers={"Cache-Control": "no-store"})


def verify_qr(db: Session, collector: User, code: str) -> PickupRequest:
    """Verify a signed challenge and advance ASSIGNED -> IN_PROGRESS once."""
    invalid = HTTPException(status_code=400, detail="Invalid or expired pickup verification code.")
    code = code.strip()
    now = int(time.time())
    if code.startswith("RG1."):
        try:
            claims = jwt.decode(code[4:], _qr_signing_key(),
                                algorithms=[settings.JWT_ALGORITHM],
                                audience="renewgrid-collector", issuer="renewgrid")
            if claims.get("purpose") != "pickup_handoff" or claims.get("collector_id") != collector.id:
                raise invalid
            pickup_id = int(claims["sub"])
        except (JWTError, ValueError, TypeError, KeyError):
            raise invalid
    else:
        match = _MANUAL_PATTERN.fullmatch(code)
        if not match:
            raise invalid
        pickup_id = int(match.group(1))

    pickup = pickup_repo.get_by_id(db, pickup_id)
    if not pickup or pickup.collector_id != collector.id:
        raise invalid
    if pickup.status != PickupStatus.ASSIGNED:
        raise HTTPException(status_code=409, detail="Pickup is no longer awaiting handoff verification.")
    if not code.startswith("RG1."):
        expected = _manual_code(pickup.id, collector.id, now // _QR_WINDOW_SECONDS)
        if not hmac.compare_digest(code, expected):
            raise invalid

    # Compare-and-swap protects against replay/concurrent scans across workers.
    changed = db.execute(
        update(PickupRequest)
        .where(PickupRequest.id == pickup.id,
               PickupRequest.collector_id == collector.id,
               PickupRequest.status == PickupStatus.ASSIGNED)
        .values(status=PickupStatus.IN_PROGRESS)
    )
    if changed.rowcount != 1:
        db.rollback()
        raise HTTPException(status_code=409, detail="Pickup has already been verified or changed.")
    pickup_repo.add_history(db, pickup.id, PickupStatus.IN_PROGRESS, collector.id,
                            "Assigned collector verified pickup handoff code")
    db.commit()
    db.expire_all()
    return pickup_repo.get_by_id(db, pickup_id)


def submit_review(db: Session, current_user: User, pickup_id: int, rating: int, comment: Optional[str]) -> Dict[str, Any]:
    pickup = pickup_repo.get_by_id(db, pickup_id)
    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found.")
    if pickup.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only review your own pickups.")

    existing = pickup_repo.get_review_by_user_and_pickup(db, current_user.id, pickup_id)
    if existing:
        raise HTTPException(status_code=409, detail="You have already reviewed this pickup.")

    review = pickup_repo.add_review(db, current_user.id, pickup_id, rating, comment)
    db.commit()
    return {
        "message": "Review submitted successfully.",
        "review_id": review.id,
        "rating": review.rating,
        "comment": review.comment,
    }

def _get_authorized_pickup(
    db: Session,
    current_user: User,
    pickup_id: int,
) -> PickupRequest:
    """Return a pickup only when the caller is an authorized participant."""
    pickup = pickup_repo.get_by_id(db, pickup_id)
    if pickup is None:
        raise HTTPException(
            status_code=404,
            detail="Pickup not found.",
        )
    is_authorized = (
        current_user.role == UserRole.ADMIN
        or pickup.user_id == current_user.id
        or (
            current_user.role == UserRole.COLLECTOR
            and pickup.collector_id == current_user.id
        )
        or (
            current_user.role == UserRole.RECYCLER
            and pickup.recycler_id == current_user.id
        )
    )
    if not is_authorized:
        raise HTTPException(
            status_code=404,
            detail="Pickup not found.",
        )
    return pickup


def get_pickup_by_id(
    db: Session,
    current_user: User,
    pickup_id: int,
) -> PickupRequest:
    return _get_authorized_pickup(
        db, current_user, pickup_id
    )


def cancel_pickup(db: Session, current_user: User, pickup_id: int) -> PickupRequest:
    pickup = pickup_repo.get_by_user_and_id(db, current_user.id, pickup_id)
    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found.")
    if pickup.status not in (PickupStatus.PENDING, PickupStatus.ASSIGNED):
        raise HTTPException(status_code=400, detail=f"Cannot cancel a pickup in '{pickup.status}' status.")
    
    pickup.status = PickupStatus.CANCELLED
    pickup_repo.add_history(db, pickup.id, PickupStatus.CANCELLED, current_user.id, "Cancelled by user")
    db.commit()
    db.refresh(pickup)
    return pickup


def track_pickup(
    db: Session,
    current_user: User,
    pickup_id: int,
) -> Dict[str, Any]:
    pickup = _get_authorized_pickup(
        db, current_user, pickup_id
    )
    return {
        "pickup_id": pickup.id,
        "current_status": pickup.status,
        "timeline": [
            {
                "status": history.status,
                "note": history.note,
                "changed_at": history.changed_at.isoformat(),
            }
            for history in pickup.status_history
        ],
    }
