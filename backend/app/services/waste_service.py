"""
services/waste_service.py — Business logic for waste uploads.
"""
import random
from pathlib import Path
from typing import List, Optional, Tuple

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.waste import WasteUpload, WasteCategory
from app.repositories.waste_repository import waste_repo
from app.core.upload_security import (
    prepare_image,
    save_prepared_image,
    delete_uploaded_path,
)

_CATEGORY_PRICE_RATES = {
    "Laptops & Computers":      {"base": 8000.0, "per_kg": 500.0, "confidence": 0.92},
    "Mobile Phones":            {"base": 6500.0, "per_kg": 500.0, "confidence": 0.95},
    "Monitors & Displays":      {"base": 1200.0, "per_kg": 150.0, "confidence": 0.88},
    "Printers & Peripherals":   {"base": 800.0,  "per_kg": 100.0, "confidence": 0.85},
    "Circuit Boards":           {"base": 1000.0, "per_kg": 1500.0,"confidence": 0.93},
    "Batteries":                {"base": 300.0,  "per_kg": 250.0, "confidence": 0.90},
    "Mixed Electronics":        {"base": 400.0,  "per_kg": 150.0, "confidence": 0.80},
}


def _get_pricing_rule_from_db(db, category: str):
    """Attempt to load an active PricingRule from the database for the given category."""
    try:
        from app.models.core import PricingRule
        rule = (
            db.query(PricingRule)
            .filter(PricingRule.category == category, PricingRule.active == True)
            .first()
        )
        return rule
    except Exception:
        return None


def _deterministic_ai(category: str, condition: str, weight: float, db=None) -> dict:
    """
    Pricing logic that first tries admin-defined PricingRule from DB,
    then falls back to hardcoded rates.
    """
    cond = (condition or "").lower()
    price = 0.0
    confidence = 0.90

    # Try to use admin-defined pricing rule from database
    rule = _get_pricing_rule_from_db(db, category) if db else None

    if rule:
        # Determine condition multiplier
        if "not working" in cond or "broken" in cond or "dead" in cond:
            multiplier = rule.condition_multiplier_broken
        elif "partially" in cond or "damaged" in cond:
            multiplier = rule.condition_multiplier_partial
        else:
            multiplier = rule.condition_multiplier_working

        price = (rule.base_price + rule.per_kg_rate * weight) * multiplier
        confidence = 0.93
    else:
        # Fallback to hardcoded rates
        rates = _CATEGORY_PRICE_RATES.get(category, _CATEGORY_PRICE_RATES["Mixed Electronics"])
        if "not working" in cond or "broken" in cond:
            multiplier = 0.3
        elif "partially" in cond:
            multiplier = 0.6
        else:
            multiplier = 1.0
        price = (rates["base"] + rates["per_kg"] * weight) * multiplier
        confidence = rates["confidence"]

    price = round(max(price, 1.0), 2)

    return {
        "ai_detected_type": f"AI: {category}",
        "ai_confidence": confidence,
        "estimated_price": price,
        "estimated_credit_points": max(1, int(weight * 10)),
        "estimated_co2_saved": round(weight * 0.5, 2),
    }

def _mock_ai(category: str, weight: float = 1.0, condition: str = None, db=None) -> dict:
    return _deterministic_ai(category, condition, weight, db)


from app.services.event_service import handle_waste_uploaded
from fastapi import BackgroundTasks

def create_waste_upload(
    db: Session,
    user_id: int,
    title: str,
    category: WasteCategory,
    estimated_weight: float,
    background_tasks: BackgroundTasks,
    description: Optional[str] = None,
    condition: Optional[str] = None,
    quantity: int = 1,
    images: List[UploadFile] = None,
) -> WasteUpload:
    if images and len(images) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 images allowed.",
        )

    # Validate every image before making database changes.
    prepared_images = [
        prepare_image(image)
        for image in (images or [])
    ]

    ai = _mock_ai(
        category,
        estimated_weight,
        condition,
        db=db,
    )

    saved_paths: List[str] = []
    try:
        waste = waste_repo.create(
            db=db,
            user_id=user_id,
            title=title,
            description=description,
            category=category,
            condition=condition,
            estimated_weight=estimated_weight,
            quantity=quantity,
            ai_detected_type=ai["ai_detected_type"],
            ai_confidence=ai["ai_confidence"],
            estimated_price=ai["estimated_price"],
            estimated_credit_points=ai["estimated_credit_points"],
            estimated_co2_saved=ai["estimated_co2_saved"],
        )

        for idx, png_bytes in enumerate(prepared_images):
            path = save_prepared_image(png_bytes, folder="waste")
            saved_paths.append(path)
            waste_repo.add_image(db, waste.id, path, (idx == 0))

        db.commit()
        db.refresh(waste)
    except Exception:
        db.rollback()
        for path in saved_paths:
            delete_uploaded_path(path)
        raise

    # Trigger Event
    handle_waste_uploaded(background_tasks, user_id, waste.id)

    return waste

def get_user_uploads(db: Session, user_id: int, page: int, page_size: int) -> Tuple[int, List[WasteUpload]]:
    return waste_repo.get_by_user_paginated(db, user_id, page, page_size)

def get_waste_by_id(db: Session, waste_id: int, current_user: User) -> WasteUpload:
    waste = waste_repo.get_by_id(db, waste_id)
    if not waste:
        raise HTTPException(status_code=404, detail="Waste upload not found.")
    if waste.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied.")
    return waste
