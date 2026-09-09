"""
services/pickup_service.py — Business logic for pickup requests.
"""
import io
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

def generate_qr(db: Session, current_user: User, pickup_id: int) -> StreamingResponse:
    pickup = pickup_repo.get_by_id(db, pickup_id)
    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found.")
    if pickup.user_id != current_user.id and current_user.role not in (UserRole.ADMIN, UserRole.COLLECTOR, UserRole.RECYCLER):
        raise HTTPException(status_code=403, detail="Access denied.")

    qr_data = (
        f"RenewGrid Pickup\n"
        f"ID: {pickup.id}\n"
        f"Status: {pickup.status.value}\n"
        f"Address: {pickup.address}\n"
        f"Created: {pickup.created_at.strftime('%Y-%m-%d %H:%M')}"
    )

    img = qrcode.make(qr_data)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png",
                             headers={"Content-Disposition": f"inline; filename=pickup_{pickup_id}_qr.png"})

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

def get_pickup_by_id(db: Session, current_user: User, pickup_id: int) -> PickupRequest:
    pickup = pickup_repo.get_by_id(db, pickup_id)
    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found.")
    if pickup.user_id != current_user.id and current_user.role not in (UserRole.ADMIN, UserRole.COLLECTOR, UserRole.RECYCLER):
        raise HTTPException(status_code=403, detail="Access denied.")
    return pickup

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

def track_pickup(db: Session, current_user: User, pickup_id: int) -> Dict[str, Any]:
    pickup = pickup_repo.get_by_id(db, pickup_id)
    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found.")
    if pickup.user_id != current_user.id and current_user.role not in (UserRole.ADMIN, UserRole.COLLECTOR, UserRole.RECYCLER):
        raise HTTPException(status_code=403, detail="Access denied.")

    return {
        "pickup_id": pickup.id,
        "current_status": pickup.status,
        "timeline": [
            {"status": h.status, "note": h.note, "changed_at": h.changed_at.isoformat()}
            for h in pickup.status_history
        ],
    }
