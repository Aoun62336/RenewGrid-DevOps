from typing import Tuple, List, Optional
from sqlalchemy.orm import Session
from app.models.core import PickupRequest, PickupStatus, PickupStatusHistory, PickupReview

class PickupRepository:
    def create(self, db: Session, user_id: int, waste_upload_id: int, address: str, pickup_date, notes: Optional[str]) -> PickupRequest:
        pickup = PickupRequest(
            user_id=user_id, waste_upload_id=waste_upload_id, address=address,
            pickup_date=pickup_date, notes=notes, status=PickupStatus.PENDING
        )
        db.add(pickup)
        db.flush()
        return pickup
        
    def add_history(self, db: Session, pickup_id: int, status: PickupStatus, changed_by_id: int, note: Optional[str]):
        db.add(PickupStatusHistory(pickup_id=pickup_id, status=status, note=note, changed_by_id=changed_by_id))
        
    def get_by_user_paginated(self, db: Session, user_id: int, page: int, page_size: int,
                               status=None, from_date=None, to_date=None):
        from datetime import datetime, timezone, timedelta
        q = db.query(PickupRequest).filter(PickupRequest.user_id == user_id)
        if status:
            q = q.filter(PickupRequest.status == status)
        if from_date:
            q = q.filter(PickupRequest.created_at >= datetime(from_date.year, from_date.month, from_date.day, tzinfo=timezone.utc))
        if to_date:
            end = datetime(to_date.year, to_date.month, to_date.day, tzinfo=timezone.utc) + timedelta(days=1)
            q = q.filter(PickupRequest.created_at < end)
        total = q.count()
        items = q.order_by(PickupRequest.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return total, items

        
    def get_all_paginated(self, db: Session, page: int, page_size: int, status: Optional[PickupStatus] = None) -> Tuple[int, List[PickupRequest]]:
        q = db.query(PickupRequest)
        if status:
            q = q.filter(PickupRequest.status == status)
        total = q.count()
        items = q.order_by(PickupRequest.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return total, items
        
    def get_total_count(self, db: Session) -> int:
        return db.query(PickupRequest).count()
        
    def get_completed_count(self, db: Session) -> int:
        return db.query(PickupRequest).filter(PickupRequest.status == PickupStatus.COMPLETED).count()
        
    def get_by_id(self, db: Session, pickup_id: int) -> Optional[PickupRequest]:
        return db.query(PickupRequest).filter(PickupRequest.id == pickup_id).first()
        
    def get_by_user_and_id(self, db: Session, user_id: int, pickup_id: int) -> Optional[PickupRequest]:
        return db.query(PickupRequest).filter(PickupRequest.id == pickup_id, PickupRequest.user_id == user_id).first()

    def get_reviews(self, db: Session, pickup_id: Optional[int]) -> List[PickupReview]:
        q = db.query(PickupReview)
        if pickup_id is not None:
            q = q.filter(PickupReview.pickup_id == pickup_id)
        return q.order_by(PickupReview.created_at.desc()).all()

    def get_reviews_for_collector(self, db: Session, collector_id: int) -> List[PickupReview]:
        return db.query(PickupReview).join(PickupRequest).filter(PickupRequest.collector_id == collector_id).order_by(PickupReview.created_at.desc()).all()
        
    def get_review_by_user_and_pickup(self, db: Session, user_id: int, pickup_id: int) -> Optional[PickupReview]:
        return db.query(PickupReview).filter(PickupReview.pickup_id == pickup_id, PickupReview.user_id == user_id).first()
        
    def add_review(self, db: Session, user_id: int, pickup_id: int, rating: int, comment: Optional[str]) -> PickupReview:
        review = PickupReview(pickup_id=pickup_id, user_id=user_id, rating=rating, comment=comment)
        db.add(review)
        db.flush()
        return review

pickup_repo = PickupRepository()
