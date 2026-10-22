"""
schemas/pickup.py — Pydantic schemas for pickup lifecycle.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_serializer
from app.models.core import PickupStatus
from app.schemas.auth import UserPublic
from app.core.media_security import media_url


class PickupCreate(BaseModel):
    waste_id: int
    pickup_date: Optional[datetime] = None
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None


class StatusHistoryOut(BaseModel):
    id: int
    status: PickupStatus
    note: Optional[str]
    changed_at: datetime
    model_config = {"from_attributes": True}


class CollectorProofOut(BaseModel):
    id: int
    image_url: str
    notes: Optional[str]
    uploaded_at: datetime
    model_config = {"from_attributes": True}

    @field_serializer("image_url")
    def serialize_image_url(self, value: str) -> str | None:
        return media_url(value)


class PickupResponse(BaseModel):
    id: int
    user_id: int
    waste_upload_id: int
    collector_id: Optional[int]
    recycler_id: Optional[int]
    recycler: Optional[UserPublic] = None
    address: str
    latitude: Optional[float]
    longitude: Optional[float]
    pickup_date: Optional[datetime]
    notes: Optional[str]
    status: PickupStatus
    final_collected_weight: Optional[float]
    final_price: Optional[float]
    collector_notes: Optional[str]
    status_history: List[StatusHistoryOut] = []
    collector_proof: Optional[CollectorProofOut] = None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class StatusUpdateIn(BaseModel):
    note: Optional[str] = None


class WeightUpdateIn(BaseModel):
    final_collected_weight: float
    collector_notes: Optional[str] = None
