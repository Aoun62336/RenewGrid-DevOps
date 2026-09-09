"""
models/waste.py — WasteUpload and WasteImage models.
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class WasteCategory(str, enum.Enum):
    LAPTOPS   = "Laptops & Computers"
    MOBILE    = "Mobile Phones"
    MONITORS  = "Monitors & Displays"
    PRINTERS  = "Printers & Peripherals"
    CIRCUITS  = "Circuit Boards"
    BATTERIES = "Batteries"
    MIXED     = "Mixed Electronics"


class WasteUpload(Base):
    __tablename__ = "waste_uploads"

    id: Mapped[int]       = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int]  = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    title: Mapped[str]    = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[WasteCategory] = mapped_column(Enum(WasteCategory, name="wastecategory"), nullable=False)
    condition: Mapped[str | None]   = mapped_column(String(100), nullable=True)
    estimated_weight: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int]           = mapped_column(Integer, default=1)

    # AI inference placeholders
    ai_detected_type: Mapped[str | None]  = mapped_column(String(255), nullable=True)
    ai_confidence: Mapped[float | None]   = mapped_column(Float, nullable=True)
    estimated_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_credit_points: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_co2_saved: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    owner           = relationship("User", back_populates="waste_uploads")
    images          = relationship("WasteImage", back_populates="waste", cascade="all, delete-orphan")
    pickup_requests = relationship("PickupRequest", back_populates="waste")


class WasteImage(Base):
    __tablename__ = "waste_images"

    id: Mapped[int]          = mapped_column(Integer, primary_key=True, index=True)
    waste_id: Mapped[int]    = mapped_column(Integer, ForeignKey("waste_uploads.id"), nullable=False)
    image_url: Mapped[str]   = mapped_column(String(1000), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    waste = relationship("WasteUpload", back_populates="images")
