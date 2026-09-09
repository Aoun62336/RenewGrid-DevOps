from typing import Tuple, List, Optional
from sqlalchemy.orm import Session
from app.models.user import User, UserRole

class UserRepository:
    def get_total_count(self, db: Session) -> int:
        return db.query(User).count()
        
    def get_active_count_by_role(self, db: Session, role: UserRole) -> int:
        return db.query(User).filter(User.role == role, User.is_active == True).count()
        
    def get_paginated(self, db: Session, page: int, page_size: int, role: Optional[UserRole] = None, is_active: Optional[bool] = None, search: Optional[str] = None) -> Tuple[int, List[User]]:
        from sqlalchemy import or_
        q = db.query(User)
        if role:
            q = q.filter(User.role == role)
        if is_active is not None:
            q = q.filter(User.is_active == is_active)
        if search:
            pattern = f"%{search}%"
            q = q.filter(or_(User.full_name.ilike(pattern), User.email.ilike(pattern)))
        total = q.count()
        items = q.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return total, items
        
    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
        
    def get_by_id_and_role(self, db: Session, user_id: int, role: UserRole) -> Optional[User]:
        return db.query(User).filter(User.id == user_id, User.role == role).first()
        
    def get_active_collector(self, db: Session, collector_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == collector_id, User.role == UserRole.COLLECTOR, User.is_active == True).first()
        
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, full_name: str, email: str, password_hash: str, role: UserRole) -> User:
        user = User(
            full_name=full_name,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True,
        )
        db.add(user)
        db.flush()
        return user

user_repo = UserRepository()
