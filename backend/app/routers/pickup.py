"""
routers/pickup.py — Pickup request lifecycle for Users.
Includes: create, list, get, cancel, track, review, QR code.
"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.models.core import PickupStatus
from app.schemas.pickup import PickupCreate, PickupResponse
from app.services import pickup_service

router = APIRouter()

# ─── Schemas ─────────────────────────────────────────────────────────────────
class ReviewIn(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = None

class ReviewOut(BaseModel):
    id: int
    pickup_id: int
    user_name: str
    rating: int
    comment: Optional[str]
    created_at: str

    model_config = {"from_attributes": True}

# ─── POST /pickup/create ──────────────────────────────────────────────────────
@router.post("/create", response_model=PickupResponse, status_code=201, summary="Schedule a pickup request")
def create_pickup(
    body: PickupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return pickup_service.create_pickup(db, current_user, body)

# ─── GET /pickup/my-requests ──────────────────────────────────────────────────
@router.get("/my-requests", response_model=dict, summary="My pickup request history")
def my_pickups(
    page: int              = Query(1, ge=1),
    page_size: int         = Query(10, ge=1, le=50),
    status: Optional[str]  = Query(None, description="Filter by status, e.g. COMPLETED"),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date]   = Query(None),
    db: Session            = Depends(get_db),
    current_user: User     = Depends(get_current_user),
):
    status_enum = PickupStatus(status) if status else None
    total, items = pickup_service.get_user_pickups(
        db, current_user, page, page_size, status=status_enum,
        from_date=from_date, to_date=to_date,
    )
    return {"total": total, "page": page, "page_size": page_size,
            "items": [PickupResponse.model_validate(i) for i in items]}

# ─── GET /pickup/reviews ─────────────────────────────────────────────────────
@router.get("/reviews", summary="List pickup reviews")
def list_reviews(
    pickup_id: Optional[int] = Query(None, description="Filter by pickup ID"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return pickup_service.list_reviews(db, pickup_id)

# ─── GET /pickup/qr/{pickup_id} ───────────────────────────────────────────────
@router.get("/qr/{pickup_id}", summary="Generate QR code image for a pickup")
def generate_qr(
    pickup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return pickup_service.generate_qr(db, current_user, pickup_id)

# ─── GET /pickup/qr-credentials/{pickup_id} ──────────────────────────────────
@router.get("/qr-credentials/{pickup_id}", summary="Short-lived pickup QR and manual handoff code")
def qr_credentials(
    pickup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        pickup_service.generate_qr_credentials(db, current_user, pickup_id),
        headers={"Cache-Control": "no-store"},
    )

# ─── POST /pickup/review/{pickup_id} ─────────────────────────────────────────
@router.post("/review/{pickup_id}", status_code=201, summary="Submit a review for a pickup")
def submit_review(
    pickup_id: int,
    body: ReviewIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return pickup_service.submit_review(db, current_user, pickup_id, body.rating, body.comment)

# ─── GET /pickup/{pickup_id} ──────────────────────────────────────────────────
@router.get("/{pickup_id}", response_model=PickupResponse, summary="Get pickup detail")
def get_pickup(
    pickup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return pickup_service.get_pickup_by_id(db, current_user, pickup_id)

# ─── PUT /pickup/cancel/{pickup_id} ──────────────────────────────────────────
@router.put("/cancel/{pickup_id}", response_model=PickupResponse, summary="Cancel a pending or assigned pickup")
def cancel_pickup(
    pickup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return pickup_service.cancel_pickup(db, current_user, pickup_id)

# ─── GET /pickup/track/{pickup_id} ───────────────────────────────────────────
@router.get("/track/{pickup_id}", response_model=dict, summary="Live status + timeline")
def track_pickup(
    pickup_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return pickup_service.track_pickup(db, current_user, pickup_id)
