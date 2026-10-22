"""
routers/collector.py — Collector-specific actions.
Role guard: only users with role=COLLECTOR can access these.
State machine: ASSIGNED → ACCEPTED → IN_ROUTE → IN_PROGRESS → COLLECTED → COMPLETED
"""
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.core.limiter import limiter
from app.models.user import User, UserRole
from app.schemas.pickup import PickupResponse, WeightUpdateIn
from app.services import collector_service, pickup_service

router = APIRouter()

# ─── Schemas ─────────────────────────────────────────────────────────────────
class VerifyQRIn(BaseModel):
    code: str = Field(min_length=8, max_length=2048)


class AvailabilityIn(BaseModel):
    is_available: bool

class RejectIn(BaseModel):
    reason: Optional[str] = None

# ─── POST /collector/verify-qr ─────────────────────────────────────────────────
@router.post("/verify-qr", response_model=PickupResponse, summary="Verify assigned pickup handoff")
@limiter.limit("6/minute")
def verify_pickup_qr(
    request: Request,
    body: VerifyQRIn,
    db: Session = Depends(get_db),
    collector: User = Depends(require_role(UserRole.COLLECTOR)),
):
    return pickup_service.verify_qr(db, collector, body.code)

# ─── GET /collector/pickups ───────────────────────────────────────────────────
@router.get("/pickups", response_model=dict, summary="My assigned pickups")
def assigned_pickups(
    page: int      = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session    = Depends(get_db),
    collector: User = Depends(require_role(UserRole.COLLECTOR)),
):
    total, items = collector_service.get_assigned_pickups(db, collector, page, page_size)
    return {"total": total, "page": page, "page_size": page_size,
            "items": [PickupResponse.model_validate(i) for i in items]}

# ─── PUT /collector/accept/{pickup_id} — ASSIGNED → IN_PROGRESS (Start Processing) ──
@router.put("/accept/{pickup_id}", response_model=PickupResponse, summary="Accept assignment: ASSIGNED → IN_PROGRESS")
def accept_pickup(
    pickup_id: int,
    db: Session = Depends(get_db),
    collector: User = Depends(require_role(UserRole.COLLECTOR)),
):
    return collector_service.accept_pickup(db, collector, pickup_id)

# ─── PUT /collector/reject/{pickup_id} — ASSIGNED/IN_PROGRESS → PENDING ──────
@router.put("/reject/{pickup_id}", summary="Reject assignment: sends back to Admin for re-assignment")
def reject_pickup(
    pickup_id: int,
    body: RejectIn = RejectIn(),
    db: Session = Depends(get_db),
    collector: User = Depends(require_role(UserRole.COLLECTOR)),
):
    return collector_service.reject_pickup(db, collector, pickup_id, body.reason)

# ─── PUT /collector/collect/{pickup_id} — PROOF_UPLOADED → COLLECTED ─────────
@router.put("/collect/{pickup_id}", response_model=PickupResponse, summary="Collect waste: PROOF_UPLOADED → COLLECTED")
def collect_waste(
    pickup_id: int,
    db: Session = Depends(get_db),
    collector: User = Depends(require_role(UserRole.COLLECTOR)),
):
    return collector_service.collect_waste(db, collector, pickup_id)

# ─── PUT /collector/handover/{pickup_id} — COLLECTED → DELIVERED ──────────────
@router.put("/handover/{pickup_id}", response_model=PickupResponse, summary="Handover to recycler: COLLECTED → DELIVERED")
def handover_to_recycler(
    pickup_id: int,
    db: Session = Depends(get_db),
    collector: User = Depends(require_role(UserRole.COLLECTOR)),
):
    return collector_service.handover(db, collector, pickup_id)

# ─── PUT /collector/update-weight/{pickup_id} ────────────────────────────────
@router.put("/update-weight/{pickup_id}", response_model=PickupResponse, summary="Update actual collected weight")
def update_weight(
    pickup_id: int,
    body: WeightUpdateIn,
    db: Session = Depends(get_db),
    collector: User = Depends(require_role(UserRole.COLLECTOR)),
):
    return collector_service.update_weight(db, collector, pickup_id, body)

# ─── POST /collector/upload-proof/{pickup_id} ────────────────────────────────
@router.post("/upload-proof/{pickup_id}", summary="Upload collection proof image")
def upload_proof(
    pickup_id: int,
    notes: Optional[str] = Form(None),
    image: UploadFile     = File(...),
    db: Session           = Depends(get_db),
    collector: User       = Depends(require_role(UserRole.COLLECTOR)),
):
    return collector_service.upload_proof(db, collector, pickup_id, notes, image)

# ─── PUT /collector/availability ─────────────────────────────────────────────
@router.put("/availability", summary="Update collector availability status")
def update_availability(
    body: AvailabilityIn,
    db: Session = Depends(get_db),
    collector: User = Depends(require_role(UserRole.COLLECTOR)),
):
    return collector_service.update_availability(db, collector, body.is_available)

# ─── GET /collector/reviews ───────────────────────────────────────────────────
@router.get("/reviews", summary="Get all reviews left by users for my pickups")
def get_my_reviews(
    db: Session = Depends(get_db),
    collector: User = Depends(require_role(UserRole.COLLECTOR)),
):
    return collector_service.get_reviews(db, collector)
