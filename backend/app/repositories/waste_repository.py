from typing import Tuple, List, Optional
from sqlalchemy.orm import Session
from app.models.waste import WasteUpload, WasteImage

class WasteRepository:
    def create(
        self, db: Session, user_id: int, title: str, description: Optional[str],
        category, condition: Optional[str], estimated_weight: float, quantity: int,
        ai_detected_type: str, ai_confidence: float, estimated_price: float,
        estimated_credit_points: Optional[int] = None, estimated_co2_saved: Optional[float] = None
    ) -> WasteUpload:
        waste = WasteUpload(
            user_id=user_id, title=title, description=description, category=category,
            condition=condition, estimated_weight=estimated_weight, quantity=quantity,
            ai_detected_type=ai_detected_type, ai_confidence=ai_confidence, estimated_price=estimated_price,
            estimated_credit_points=estimated_credit_points, estimated_co2_saved=estimated_co2_saved
        )
        db.add(waste)
        db.flush()
        return waste
    
    def add_image(self, db: Session, waste_id: int, image_url: str, is_primary: bool) -> WasteImage:
        img = WasteImage(waste_id=waste_id, image_url=image_url, is_primary=is_primary)
        db.add(img)
        return img
    
    def get_total_count(self, db: Session) -> int:
        return db.query(WasteUpload).count()

    def get_by_user_paginated(self, db: Session, user_id: int, page: int, page_size: int) -> Tuple[int, List[WasteUpload]]:
        q = db.query(WasteUpload).filter(WasteUpload.user_id == user_id)
        total = q.count()
        items = q.order_by(WasteUpload.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return total, items
        
    def get_all_paginated(self, db: Session, page: int, page_size: int) -> Tuple[int, List[WasteUpload]]:
        q = db.query(WasteUpload)
        total = q.count()
        items = q.order_by(WasteUpload.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return total, items
        
    def get_by_id(self, db: Session, waste_id: int) -> Optional[WasteUpload]:
        return db.query(WasteUpload).filter(WasteUpload.id == waste_id).first()

waste_repo = WasteRepository()
