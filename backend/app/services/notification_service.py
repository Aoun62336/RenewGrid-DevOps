"""
services/notification_service.py — Background-safe notification delivery.
"""
import logging
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.core import Notification

logger = logging.getLogger(__name__)

def create_notification_bg(user_id: int, title: str, message: str) -> None:
    """
    Create a Notification row asynchronously.
    Designed to run inside a FastAPI BackgroundTask — opens its own DB
    session so the foreground response is never blocked.
    """
    db: Session = SessionLocal()
    try:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message
        )
        db.add(notif)
        db.commit()
        logger.info("Notification created for user_id=%d: %s", user_id, title)
    except Exception:
        db.rollback()
        logger.exception("Failed to create notification for user_id=%d", user_id)
    finally:
        db.close()
