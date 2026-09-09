"""
routers/notifications.py — Notification management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.core import Notification
from app.schemas.notification import NotificationCreate, NotificationResponse

router = APIRouter()

@router.post("/", response_model=NotificationResponse, status_code=201, summary="Create a notification")
def create_notification(
    payload: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can manually create notifications")

    notification = Notification(
        user_id=payload.user_id,
        title=payload.title,
        message=payload.message
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


@router.get("/me", response_model=dict, summary="Get current user notifications")
def get_my_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Notification).filter(Notification.user_id == current_user.id)
    total = q.count()
    notifications = q.order_by(Notification.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [NotificationResponse.model_validate(n) for n in notifications]
    }


@router.patch("/{notification_id}/read", response_model=NotificationResponse, summary="Mark notification as read")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification
