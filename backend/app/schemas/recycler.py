"""
schemas/recycler.py — Schemas for the recycler module.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.core import PickupStatus


class ProcessStartIn(BaseModel):
    decision: str           # recycle / refurbish
    processing_notes: Optional[str] = None


class ProcessUpdateIn(BaseModel):
    outcome: PickupStatus          # RECYCLED or COMPLETED
    decision: Optional[str] = None # "recycle" or "refurbish" — stores the human decision
    revenue_generated: Optional[float] = None
    processing_notes: Optional[str] = None


class ProcessingRecordOut(BaseModel):
    id: int
    pickup_id: int
    recycler_id: int
    decision: str
    outcome: Optional[PickupStatus]
    processing_notes: Optional[str]
    revenue_generated: Optional[float]
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class InventoryItemOut(BaseModel):
    id: int
    recycler_id: int
    pickup_id: int
    item_description: Optional[str]
    weight_kg: Optional[float]
    status: str
    created_at: datetime
    model_config = {"from_attributes": True}
