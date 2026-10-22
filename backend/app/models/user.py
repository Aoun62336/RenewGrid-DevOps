"""
models/user.py — SQLAlchemy ORM model for the `users` table.
"""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class UserRole(str, enum.Enum):
    USER      = "user"
    COLLECTOR = "collector"
    RECYCLER  = "recycler"
    ADMIN     = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int]    = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None]      = mapped_column(Text, nullable=True)
    profile_image: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    password_hash: Mapped[str]   = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole]       = mapped_column(Enum(UserRole, name="userrole"), nullable=False, default=UserRole.USER)
    is_active: Mapped[bool]      = mapped_column(Boolean, default=True, nullable=False)
    is_available: Mapped[bool]   = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    waste_uploads = relationship("WasteUpload", back_populates="owner")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role}>"


class AuthSession(Base):
    """Revocable, rotating refresh-session record."""

    __tablename__ = "auth_sessions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_digest: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
