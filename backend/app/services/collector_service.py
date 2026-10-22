"""
services/collector_service.py — Business logic for collector actions.
State machine: ASSIGNED → ACCEPTED → IN_ROUTE → IN_PROGRESS → COLLECTED → COMPLETED
"""
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.core import CollectorProof, PickupRequest, PickupStatus
from app.schemas.pickup import WeightUpdateIn
from app.repositories.collector_repository import collector_repo
from app.repositories.pickup_repository import pickup_repo
from app.core.upload_security import (
    prepare_image,
    save_prepared_image,
    delete_uploaded_path,
)
from app.core.media_security import media_url

def _get_my_pickup(db: Session, pickup_id: int, collector_id: int) -> PickupRequest:
    pickup = collector_repo.get_my_pickup(db, pickup_id, collector_id)
    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not assigned to you.")
    return pickup

def get_assigned_pickups(db: Session, collector: User, page: int, page_size: int) -> Tuple[int, List[PickupRequest]]:
    return collector_repo.get_assigned_pickups(db, collector.id, page, page_size)

# ─── State: ASSIGNED → ACCEPTED (Automatically transitions to IN_PROGRESS/Start Processing) ───
def accept_pickup(db: Session, collector: User, pickup_id: int) -> PickupRequest:
    pickup = _get_my_pickup(db, pickup_id, collector.id)
    if pickup.status in (PickupStatus.ACCEPTED, PickupStatus.IN_PROGRESS):
        return pickup  # idempotent
    if pickup.status != PickupStatus.ASSIGNED:
        raise HTTPException(status_code=400, detail=f"Pickup must be ASSIGNED to accept (current: {pickup.status.value}).")
    
    # Automatically transition to IN_PROGRESS as requested
    pickup.status = PickupStatus.IN_PROGRESS
    pickup_repo.add_history(db, pickup.id, PickupStatus.IN_PROGRESS, collector.id, "Collector accepted & started processing")
    db.commit()
    db.refresh(pickup)
    return pickup

# ─── State: ACCEPTED/IN_PROGRESS → REJECTED ────────────────────────────────────
def reject_pickup(db: Session, collector: User, pickup_id: int, reason: Optional[str] = None) -> Dict[str, Any]:
    pickup = _get_my_pickup(db, pickup_id, collector.id)
    allowed = (PickupStatus.ASSIGNED, PickupStatus.ACCEPTED, PickupStatus.IN_PROGRESS)
    if pickup.status not in allowed:
        raise HTTPException(status_code=400, detail=f"Cannot reject a pickup in '{pickup.status.value}' status.")
    
    pickup.collector_id = None
    pickup.status = PickupStatus.PENDING
    pickup_repo.add_history(db, pickup.id, PickupStatus.PENDING, collector.id, f"Collector rejected: {reason or 'No reason given'}")
    db.commit()
    return {"message": f"Pickup #{pickup_id} rejected.", "pickup_id": pickup_id}

# ─── State: IN_PROGRESS → PROOF_UPLOADED ───────────────────────────────────────
def upload_proof(
    db: Session,
    collector: User,
    pickup_id: int,
    notes: Optional[str],
    image: UploadFile,
) -> Dict[str, str]:
    pickup = _get_my_pickup(
        db,
        pickup_id,
        collector.id,
    )
    if pickup.status not in (
        PickupStatus.IN_PROGRESS,
        PickupStatus.PROOF_UPLOADED,
    ):
        if pickup.status == PickupStatus.PROCESSING:
            raise HTTPException(
                status_code=400,
                detail="The recycler has already started processing this waste. You can no longer upload proof.",
            )
        raise HTTPException(
            status_code=400,
            detail=f"Must be in 'Start Processing' (IN_PROGRESS) status to upload proof (current: {pickup.status.value}).",
        )

    prepared = prepare_image(image)
    previous_path = (
        pickup.collector_proof.image_url
        if pickup.collector_proof
        else None
    )
    new_path = save_prepared_image(
        prepared,
        folder="proofs",
    )
    try:
        proof = pickup.collector_proof
        if proof:
            proof.image_url = new_path
            proof.notes = notes
        else:
            db.add(CollectorProof(pickup_id=pickup_id, image_url=new_path, notes=notes))

        pickup.status = PickupStatus.PROOF_UPLOADED
        pickup_repo.add_history(
            db, pickup.id, PickupStatus.PROOF_UPLOADED, collector.id,
            "Collector uploaded proof image",
        )
        db.commit()
    except Exception:
        db.rollback()
        delete_uploaded_path(new_path)
        raise HTTPException(
            status_code=500,
            detail="Failed to save proof. Please try again.",
        )

    if previous_path and previous_path != new_path:
        delete_uploaded_path(previous_path)

    signed_url = media_url(new_path)
    return {
        "message": "Proof uploaded successfully.",
        "image_url": signed_url or new_path,
        "pickup_id": pickup_id,
    }

# ─── State: PROOF_UPLOADED → COLLECTED ─────────────────────────────────────────
def collect_waste(db: Session, collector: User, pickup_id: int) -> PickupRequest:
    pickup = _get_my_pickup(db, pickup_id, collector.id)
    if pickup.status == PickupStatus.COLLECTED:
        return pickup
    if pickup.status != PickupStatus.PROOF_UPLOADED:
        raise HTTPException(status_code=400, detail=f"Proof must be uploaded before marking as Collected (current: {pickup.status.value}).")
    
    pickup.status = PickupStatus.COLLECTED
    pickup_repo.add_history(db, pickup.id, PickupStatus.COLLECTED, collector.id, "Waste marked as Collected")
    db.commit()
    db.refresh(pickup)
    return pickup

# ─── State: COLLECTED → DELIVERED ──────────────────────────────────────────────
def handover(db: Session, collector: User, pickup_id: int) -> PickupRequest:
    pickup = _get_my_pickup(db, pickup_id, collector.id)
    if pickup.status == PickupStatus.DELIVERED:
        return pickup
    if pickup.status != PickupStatus.COLLECTED:
        raise HTTPException(status_code=400, detail=f"Waste must be Collected before handover (current: {pickup.status.value}).")
    
    pickup.status = PickupStatus.DELIVERED
    pickup_repo.add_history(db, pickup.id, PickupStatus.DELIVERED, collector.id, "Handed over to Recycler")
    db.commit()
    db.refresh(pickup)
    return pickup

def update_weight(db: Session, collector: User, pickup_id: int, body: WeightUpdateIn) -> PickupRequest:
    pickup = _get_my_pickup(db, pickup_id, collector.id)
    pickup.final_collected_weight = body.final_collected_weight
    
    # Recalculate price based on final weight
    if pickup.waste:
        from app.services.waste_service import _mock_ai
        ai_res = _mock_ai(pickup.waste.category, body.final_collected_weight, pickup.waste.condition)
        pickup.final_price = ai_res["estimated_price"]

    if body.collector_notes:
        pickup.collector_notes = body.collector_notes
    db.commit()
    db.refresh(pickup)
    return pickup

def update_availability(db: Session, collector: User, is_available: bool) -> Dict[str, Any]:
    collector.is_available = is_available
    db.commit()
    db.refresh(collector)
    status_str = "available" if collector.is_available else "unavailable"
    return {
        "message": f"Availability updated. You are now marked as {status_str}.",
        "collector_id": collector.id,
        "is_available": collector.is_available,
    }

def get_reviews(db: Session, collector: User) -> List[Dict[str, Any]]:
    reviews = pickup_repo.get_reviews_for_collector(db, collector.id)
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
