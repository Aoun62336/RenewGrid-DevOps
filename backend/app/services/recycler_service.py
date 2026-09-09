"""
services/recycler_service.py — Business logic for recycler actions.
"""
import random
from typing import List, Tuple, Dict, Any
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.core import PickupRequest, PickupStatus, ProcessingRecord, RecyclerInventory, RecyclerPayment
from app.schemas.recycler import ProcessStartIn, ProcessUpdateIn
from app.repositories.recycler_repository import recycler_repo
from app.repositories.pickup_repository import pickup_repo

def get_assigned_waste(db: Session, recycler: User, page: int, page_size: int) -> Tuple[int, List[PickupRequest]]:
    return recycler_repo.get_assigned_waste(db, recycler.id, page, page_size)

def start_processing(db: Session, recycler: User, pickup_id: int, body: ProcessStartIn) -> ProcessingRecord:
    pickup = pickup_repo.get_by_id(db, pickup_id)
    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found.")
    if pickup.status != PickupStatus.DELIVERED:
        raise HTTPException(status_code=400, detail="Pickup must be DELIVERED to start processing.")

    if pickup.recycler_id and pickup.recycler_id != recycler.id:
        raise HTTPException(status_code=403, detail="This waste batch is assigned to a different recycler.")

    if pickup.processing:
        raise HTTPException(status_code=409, detail="Processing record already exists.")

    record = recycler_repo.add_processing_record(db, pickup_id, recycler.id, body.decision, body.processing_notes)
    
    pickup.status = PickupStatus.PROCESSING
    if not pickup.recycler_id:
        pickup.recycler_id = recycler.id
    pickup_repo.add_history(db, pickup.id, PickupStatus.PROCESSING, recycler.id, f"Processing started: {body.decision}")
    db.commit()
    db.refresh(record)
    return record

from app.services.event_service import handle_pickup_completed

def update_processing(db: Session, recycler: User, pickup_id: int, body: ProcessUpdateIn, background_tasks: BackgroundTasks) -> ProcessingRecord:
    pickup = pickup_repo.get_by_id(db, pickup_id)
    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found.")

    record = pickup.processing
    if not record or record.recycler_id != recycler.id:
        raise HTTPException(status_code=404, detail="No processing record found for this recycler.")

    if body.outcome not in (PickupStatus.RECYCLED, PickupStatus.COMPLETED):
        raise HTTPException(status_code=400, detail="Outcome must be RECYCLED or COMPLETED.")

    # Mark as COMPLETED universally if it was RECYCLED
    final_outcome = PickupStatus.COMPLETED if body.outcome == PickupStatus.RECYCLED else body.outcome

    record.outcome = final_outcome
    if body.decision:
        record.decision = body.decision
    record.revenue_generated = body.revenue_generated
    if body.processing_notes:
        record.processing_notes = body.processing_notes

    pickup.status = final_outcome
    pickup_repo.add_history(db, pickup.id, final_outcome, recycler.id, f"Outcome: {final_outcome}")

    # Add to inventory
    recycler_repo.add_inventory(db, recycler.id, pickup_id, pickup.final_collected_weight, final_outcome.value.lower())

    db.commit()
    db.refresh(record)

    # ── Trigger Event ─────────────────────────────
    if body.outcome == PickupStatus.COMPLETED:
        handle_pickup_completed(background_tasks, pickup)

    return record

def get_inventory(db: Session, recycler: User, page: int, page_size: int) -> Tuple[int, List[RecyclerInventory]]:
    return recycler_repo.get_inventory(db, recycler.id, page, page_size)


def send_payment(db: Session, recycler: User, pickup_id: int, amount: float, note: str = None) -> Dict[str, Any]:
    """
    Recycler sends a monetary payment to the user for their e-waste.
    This is logged to recycler_payments and auto-appears in:
      - User Reward Wallet (Reward Payment section)
      - Admin Revenue Tracking
    """
    pickup = pickup_repo.get_by_id(db, pickup_id)
    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found.")
    if pickup.recycler_id and pickup.recycler_id != recycler.id:
        raise HTTPException(status_code=403, detail="This pickup is not assigned to you.")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be greater than zero.")

    # Idempotency: one payment per pickup per recycler
    existing = db.query(RecyclerPayment).filter(
        RecyclerPayment.pickup_id == pickup_id,
        RecyclerPayment.recycler_id == recycler.id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Payment already sent for this pickup.")

    waste_item = pickup.waste.title if pickup.waste else f"Pickup #{pickup_id}"
    payment = RecyclerPayment(
        pickup_id=pickup_id,
        user_id=pickup.user_id,
        recycler_id=recycler.id,
        amount=amount,
        waste_item=waste_item,
        note=note,
    )
    db.add(payment)
    
    # Also update the processing record's revenue_generated so it shows in history
    if pickup.processing:
        pickup.processing.revenue_generated = amount
        
    db.commit()
    db.refresh(payment)
    return {
        "message": "Payment sent successfully.",
        "payment_id": payment.id,
        "amount": payment.amount,
        "user_id": payment.user_id,
        "pickup_id": pickup_id,
    }


def get_payments_for_recycler(db: Session, recycler_id: int, page: int, page_size: int) -> Tuple[int, List[RecyclerPayment]]:
    q = db.query(RecyclerPayment).filter(RecyclerPayment.recycler_id == recycler_id).order_by(RecyclerPayment.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return total, items


def get_ai_recommendation(db: Session, pickup_id: int) -> Dict[str, Any]:
    pickup = pickup_repo.get_by_id(db, pickup_id)
    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found")
        
    weight = pickup.final_collected_weight or (pickup.waste.estimated_weight if pickup.waste else 10.0)
    
    from datetime import datetime, timezone
    age_days = (datetime.now(timezone.utc) - pickup.created_at).days if pickup.created_at else 0
    confidence = max(50.0, min(99.9, 95.0 - (age_days * 0.2) + (weight * 0.05)))
    
    category = pickup.waste.category if pickup.waste and pickup.waste.category else "Mixed Electronics"
    
    if "Laptop" in category or "Computer" in category:
        action = "Full Refurbish" if weight < 50 else "Recycle"
        reasoning = "High component reuse potential." if action == "Full Refurbish" else "End of lifecycle, extract raw materials."
        materials = [
            {"name": "Gold Recovery", "yield": "2.4g / unit", "pct": 85},
            {"name": "Copper Yield", "yield": "145g / unit", "pct": 60},
            {"name": "Palladium", "yield": "0.8g / unit", "pct": 40}
        ]
        components = [
            {"name": "Main Processor Board", "serial": f"{pickup_id}x-BC-441", "action": "Refurbish", "health": "98% Integrity", "value": "₹3500 Value", "icon": "memory", "health_icon": "check_circle", "value_icon": "payments"},
            {"name": "Li-Ion Energy Module", "serial": f"BT-{pickup_id}-LIT", "action": "Recycle", "health": "12% Life", "value": "High Cobalt", "icon": "battery_full", "health_icon": "warning", "value_icon": "recycling"}
        ]
    elif "Mobile" in category or "Phone" in category:
        action = "Partial Refurbish" if weight < 10 else "Recycle"
        reasoning = "Screens and batteries show wear, but logic boards are intact." if action == "Partial Refurbish" else "Extensive damage detected, recycle for rare earths."
        materials = [
            {"name": "Cobalt", "yield": "8g / unit", "pct": 90},
            {"name": "Silver Yield", "yield": "0.3g / unit", "pct": 75}
        ]
        components = [
            {"name": "Logic Board", "serial": f"MB-{pickup_id}-X", "action": "Refurbish", "health": "Functional", "value": "₹1500 Value", "icon": "memory", "health_icon": "check_circle", "value_icon": "payments"},
            {"name": "Display Assembly", "serial": f"SCR-{pickup_id}", "action": "Recycle", "health": "Cracked", "value": "Glass/Metal", "icon": "smartphone", "health_icon": "warning", "value_icon": "recycling"}
        ]
    else:
        action = "Recycle"
        reasoning = f"Standard recycling procedure for {category}."
        materials = [
            {"name": "Mixed Metals", "yield": f"{weight * 0.6:.1f}kg", "pct": 80},
            {"name": "Plastics", "yield": f"{weight * 0.3:.1f}kg", "pct": 60}
        ]
        components = [
            {"name": "Generic Core", "serial": f"GEN-{pickup_id}-1", "action": "Recycle", "health": "Unknown", "value": "₹500 Value", "icon": "category", "health_icon": "info", "value_icon": "payments"}
        ]

    # ── AI PRICE DUALITY RULE ──────────────────────────────────────────────────
    # The recycler-side price MUST differ from user-side by 10-20%, never identical.
    # We apply a deterministic but pseudo-random variance seeded on pickup_id.
    user_estimated_price = pickup.waste.estimated_price if pickup.waste and pickup.waste.estimated_price else None
    recycler_recommended_price = None
    if user_estimated_price and user_estimated_price > 0:
        # Use pickup_id as seed so the variance is stable across reloads
        rng = random.Random(pickup_id * 31337)
        # Variance: +10% to +20% or -10% to -20% (alternates by pickup parity)
        if pickup_id % 2 == 0:
            variance = rng.uniform(0.10, 0.20)   # recycler pays more (good deal for user)
        else:
            variance = rng.uniform(-0.20, -0.10)  # recycler pays less (fair reduction)
        recycler_recommended_price = round(user_estimated_price * (1 + variance), 2)
    
    return {
        "batch_id": f"RG-{pickup_id:04d}-EW",
        "confidence": round(confidence, 1),
        "recommended_action": action,
        "reasoning": reasoning,
        "materials": materials,
        "components": components,
        # Recycler-side recommended payment — distinct from user AI estimate
        "recommended_payment": recycler_recommended_price,
        # Original user-side estimate for reference only (shown as context)
        "user_estimated_price": round(user_estimated_price, 2) if user_estimated_price else None,
        "category": category,
        "weight": weight,
    }
