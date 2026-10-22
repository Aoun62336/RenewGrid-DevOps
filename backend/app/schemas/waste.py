"""
schemas/waste.py — Pydantic schemas for waste upload endpoints.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_serializer
from app.models.waste import WasteCategory
from app.core.media_security import media_url


class WasteImageOut(BaseModel):
    id: int
    image_url: str
    is_primary: bool
    uploaded_at: datetime
    model_config = {"from_attributes": True}

    @field_serializer("image_url")
    def serialize_image_url(self, value: str) -> str | None:
        return media_url(value)


class WasteUploadCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    category: WasteCategory
    condition: Optional[str] = None
    estimated_weight: float = Field(..., gt=0)
    quantity: int = Field(1, ge=1)


class WasteUploadResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    category: WasteCategory
    condition: Optional[str]
    estimated_weight: float
    quantity: int
    ai_detected_type: Optional[str]
    ai_confidence: Optional[float]
    estimated_price: Optional[float]
    images: List[WasteImageOut] = []
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
