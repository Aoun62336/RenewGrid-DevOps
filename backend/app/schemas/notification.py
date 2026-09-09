"""
schemas/notification.py — Pydantic schemas for notifications.
"""
from datetime import datetime
from pydantic import BaseModel

class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}
