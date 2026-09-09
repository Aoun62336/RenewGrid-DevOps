"""
routers/system.py — Master data / config endpoints (no auth required).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import UserRole
from app.models.core import PickupStatus, AppConfig

router = APIRouter()


@router.get("/roles", summary="All supported user roles")
def get_roles():
    return {"roles": [r.value for r in UserRole]}


@router.get("/status-types", summary="All supported pickup lifecycle statuses")
def get_status_types():
    return {"statuses": [s.value for s in PickupStatus]}


@router.get("/config", summary="Frontend-consumable app config")
def get_config(db: Session = Depends(get_db)):
    rows = db.query(AppConfig).all()
    config = {r.key: r.value for r in rows}
    # Defaults if DB is empty
    defaults = {
        "app_name": "RenewGrid",
        "max_images_per_upload": "5",
        "supported_categories": ",".join(c.value for c in __import__("app.models.waste", fromlist=["WasteCategory"]).WasteCategory),
        "min_pickup_notice_hours": "2",
    }
    return {**defaults, **config}


@router.get("/pricing-rates", summary="Public active pricing rates for estimation UI")
def get_pricing_rates(db: Session = Depends(get_db)):
    """Return active pricing rules for the user-facing estimation page."""
    from app.models.core import PricingRule
    rules = db.query(PricingRule).filter(PricingRule.active == True).order_by(PricingRule.category).all()
    return [
        {
            "category": r.category,
            "base_price": r.base_price,
            "per_kg_rate": r.per_kg_rate,
            "premium_rate": r.premium_rate,
            "min_weight": r.min_weight,
            "unit": r.unit,
        }
        for r in rules
    ]
