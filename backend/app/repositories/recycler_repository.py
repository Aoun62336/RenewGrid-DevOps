from typing import Tuple, List
from sqlalchemy.orm import Session
from app.models.core import PickupRequest, PickupStatus, ProcessingRecord, RecyclerInventory

class RecyclerRepository:
    def get_assigned_waste(self, db: Session, recycler_id: int, page: int, page_size: int) -> Tuple[int, List[PickupRequest]]:
        from sqlalchemy import or_
        q = db.query(PickupRequest).filter(
            PickupRequest.status.in_([PickupStatus.DELIVERED, PickupStatus.PROCESSING]),
            or_(PickupRequest.recycler_id == recycler_id, PickupRequest.recycler_id == None)
        )
        total = q.count()
        items = q.order_by(PickupRequest.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return total, items
        
    def add_processing_record(self, db: Session, pickup_id: int, recycler_id: int, decision: str, processing_notes: str) -> ProcessingRecord:
        record = ProcessingRecord(pickup_id=pickup_id, recycler_id=recycler_id, decision=decision, processing_notes=processing_notes)
        db.add(record)
        db.flush()
        return record
        
    def add_inventory(self, db: Session, recycler_id: int, pickup_id: int, weight_kg: float, status: str) -> RecyclerInventory:
        inv = RecyclerInventory(recycler_id=recycler_id, pickup_id=pickup_id, weight_kg=weight_kg, status=status)
        db.add(inv)
        db.flush()
        return inv
        
    def get_inventory(self, db: Session, recycler_id: int, page: int, page_size: int) -> Tuple[int, List[RecyclerInventory]]:
        q = db.query(RecyclerInventory).filter(RecyclerInventory.recycler_id == recycler_id)
        total = q.count()
        items = q.order_by(RecyclerInventory.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return total, items

recycler_repo = RecyclerRepository()
