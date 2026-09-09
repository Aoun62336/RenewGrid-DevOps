"""
repositories/auth_repository.py — Raw database operations for the auth module.

The repository layer is the ONLY place in the app that executes SQL queries.
Service layers call repository methods; routers never touch the DB directly.
"""
from sqlalchemy.orm import Session

from app.models.user import User


class AuthRepository:
    """Encapsulates all DB queries related to authentication."""

    # ── Reads ─────────────────────────────────────────────────────────────
    def get_by_email(self, db: Session, *, email: str) -> User | None:
        """Return the first user whose email matches, or None."""
        return db.query(User).filter(User.email == email).first()

    def get_by_id(self, db: Session, *, user_id: int) -> User | None:
        """Return the user for the given PK, or None."""
        return db.query(User).get(user_id)

    # ── Writes ────────────────────────────────────────────────────────────
    def create(
        self,
        db: Session,
        *,
        full_name: str,
        email: str,
        phone_number: str | None,
        password_hash: str,
        role,
    ) -> User:
        """
        Persist a new User row and return the refreshed ORM object.
        Callers are responsible for supplying the already-hashed password.
        """
        user = User(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            password_hash=password_hash,
            role=role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


# ── Module-level singleton ────────────────────────────────────────────────────
auth_repo = AuthRepository()
