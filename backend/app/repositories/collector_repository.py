from typing import Tuple, List, Optional
from sqlalchemy.orm import Session
from app.models.core import PickupRequest, CollectorProof

class CollectorRepository:
    def get_assigned_pickups(self, db: Session, collector_id: int, page: int, page_size: int) -> Tuple[int, List[PickupRequest]]:
        q = db.query(PickupRequest).filter(PickupRequest.collector_id == collector_id)
        total = q.count()
        items = q.order_by(PickupRequest.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return total, items
        
    def get_my_pickup(self, db: Session, pickup_id: int, collector_id: int) -> Optional[PickupRequest]:
        return db.query(PickupRequest).filter(PickupRequest.id == pickup_id, PickupRequest.collector_id == collector_id).first()

    def add_proof(self, db: Session, pickup_id: int, image_url: str, notes: Optional[str]) -> CollectorProof:
        proof = CollectorProof(pickup_id=pickup_id, image_url=image_url, notes=notes)
        db.add(proof)
        db.flush()
        return proof

collector_repo = CollectorRepository()
