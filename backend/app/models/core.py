"""
models/core.py — Canonical models for the RenewGrid lifecycle:
  PickupRequest, PickupStatusHistory, CollectorProof,
  ProcessingRecord, RecyclerInventory, Reward, AppConfig
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, DateTime, Enum, Float, ForeignKey,
    Integer, String, Text, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


# ─────────────────────────────────────────────────────────────────────────────
#  Centralised Status Enum  (single source of truth)
# ─────────────────────────────────────────────────────────────────────────────
class PickupStatus(str, enum.Enum):
    PENDING        = "PENDING"
    ASSIGNED       = "ASSIGNED"
    ACCEPTED       = "ACCEPTED"
    IN_PROGRESS    = "IN_PROGRESS"    # Also known as 'Start Processing'
    PROOF_UPLOADED = "PROOF_UPLOADED" # Collector uploaded image
    COLLECTED      = "COLLECTED"
    DELIVERED      = "DELIVERED"
    PROCESSING     = "PROCESSING"     # Recycler side
    RECYCLED       = "RECYCLED"
    COMPLETED      = "COMPLETED"
    CANCELLED      = "CANCELLED"
    REJECTED       = "REJECTED"
    IN_ROUTE       = "IN_ROUTE"       # Keeping for backwards compatibility if needed


# ─────────────────────────────────────────────────────────────────────────────
#  PickupRequest
# ─────────────────────────────────────────────────────────────────────────────
class PickupRequest(Base):
    __tablename__ = "pickup_requests"

    id: Mapped[int]            = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int]       = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    waste_upload_id: Mapped[int] = mapped_column(Integer, ForeignKey("waste_uploads.id"), nullable=False)
    collector_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    recycler_id: Mapped[int | None]  = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    address: Mapped[str]       = mapped_column(String(500), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    pickup_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None]  = mapped_column(Text, nullable=True)

    status: Mapped[PickupStatus] = mapped_column(
        Enum(PickupStatus, name="pickupstatus"),
        default=PickupStatus.PENDING,
        nullable=False,
    )

    # Collector-filled fields
    final_collected_weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    collector_notes: Mapped[str | None]  = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    user       = relationship("User", foreign_keys=[user_id])
    collector  = relationship("User", foreign_keys=[collector_id])
    recycler   = relationship("User", foreign_keys=[recycler_id])
    waste      = relationship("WasteUpload", back_populates="pickup_requests")
    status_history = relationship("PickupStatusHistory", back_populates="pickup", order_by="PickupStatusHistory.changed_at")
    collector_proof = relationship("CollectorProof", back_populates="pickup", uselist=False)
    processing = relationship("ProcessingRecord", back_populates="pickup", uselist=False)


# ─────────────────────────────────────────────────────────────────────────────
#  PickupStatusHistory  (audit trail / timeline)
# ─────────────────────────────────────────────────────────────────────────────
class PickupStatusHistory(Base):
    __tablename__ = "pickup_status_history"

    id: Mapped[int]       = mapped_column(Integer, primary_key=True, index=True)
    pickup_id: Mapped[int] = mapped_column(Integer, ForeignKey("pickup_requests.id"), nullable=False)
    status: Mapped[PickupStatus] = mapped_column(Enum(PickupStatus, name="pickupstatus"), nullable=False)
    note: Mapped[str | None]    = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    changed_by_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)

    pickup   = relationship("PickupRequest", back_populates="status_history")
    changed_by = relationship("User", foreign_keys=[changed_by_id])


# ─────────────────────────────────────────────────────────────────────────────
#  CollectorProof
# ─────────────────────────────────────────────────────────────────────────────
class CollectorProof(Base):
    __tablename__ = "collector_proofs"

    id: Mapped[int]       = mapped_column(Integer, primary_key=True, index=True)
    pickup_id: Mapped[int] = mapped_column(Integer, ForeignKey("pickup_requests.id"), unique=True, nullable=False)
    image_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    pickup = relationship("PickupRequest", back_populates="collector_proof")


# ─────────────────────────────────────────────────────────────────────────────
#  ProcessingRecord  (Recycler decision)
# ─────────────────────────────────────────────────────────────────────────────
class ProcessingRecord(Base):
    __tablename__ = "processing_records"

    id: Mapped[int]         = mapped_column(Integer, primary_key=True, index=True)
    pickup_id: Mapped[int]  = mapped_column(Integer, ForeignKey("pickup_requests.id"), unique=True, nullable=False)
    recycler_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    decision: Mapped[str]   = mapped_column(String(50))          # recycle / refurbish
    outcome: Mapped[PickupStatus | None] = mapped_column(Enum(PickupStatus, name="pickupstatus"), nullable=True)
    processing_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    revenue_generated: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    recycler = relationship("User", foreign_keys=[recycler_id])
    pickup   = relationship("PickupRequest", back_populates="processing")


# ─────────────────────────────────────────────────────────────────────────────
#  RecyclerInventory
# ─────────────────────────────────────────────────────────────────────────────
class RecyclerInventory(Base):
    __tablename__ = "recycler_inventory"

    id: Mapped[int]         = mapped_column(Integer, primary_key=True, index=True)
    recycler_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    pickup_id: Mapped[int]  = mapped_column(Integer, ForeignKey("pickup_requests.id"), nullable=False)
    item_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    weight_kg: Mapped[float | None]      = mapped_column(Float, nullable=True)
    status: Mapped[str]     = mapped_column(String(50), default="in_stock")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    recycler = relationship("User", foreign_keys=[recycler_id])
    pickup   = relationship("PickupRequest")


# ─────────────────────────────────────────────────────────────────────────────
#  Reward
# ─────────────────────────────────────────────────────────────────────────────
class Reward(Base):
    __tablename__ = "rewards"
    __table_args__ = (
        UniqueConstraint("pickup_id", name="uq_rewards_pickup_id"),
    )

    id: Mapped[int]         = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int]    = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    pickup_id: Mapped[int]  = mapped_column(Integer, ForeignKey("pickup_requests.id"), nullable=False)
    points: Mapped[int]     = mapped_column(Integer, default=0)
    co2_saved_kg: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user    = relationship("User")
    pickup  = relationship("PickupRequest")


# ─────────────────────────────────────────────────────────────────────────────
#  RecyclerPayment  (monetary payment from recycler to user)
# ─────────────────────────────────────────────────────────────────────────────
class RecyclerPayment(Base):
    __tablename__ = "recycler_payments"

    id: Mapped[int]           = mapped_column(Integer, primary_key=True, index=True)
    pickup_id: Mapped[int]    = mapped_column(Integer, ForeignKey("pickup_requests.id"), nullable=False)
    user_id: Mapped[int]      = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    recycler_id: Mapped[int]  = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    amount: Mapped[float]     = mapped_column(Float, nullable=False)          # ₹ amount
    waste_item: Mapped[str | None] = mapped_column(String(500), nullable=True) # item title
    note: Mapped[str | None]  = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user    = relationship("User", foreign_keys=[user_id])
    recycler = relationship("User", foreign_keys=[recycler_id])
    pickup  = relationship("PickupRequest")


# ─────────────────────────────────────────────────────────────────────────────
#  AppConfig  (key-value store for frontend-consumable config)
# ─────────────────────────────────────────────────────────────────────────────
class AppConfig(Base):
    __tablename__ = "app_config"

    id: Mapped[int]    = mapped_column(Integer, primary_key=True, index=True)
    key: Mapped[str]   = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PricingRule
# ─────────────────────────────────────────────────────────────────────────────
class PricingRule(Base):
    __tablename__ = "pricing_rules"

    id: Mapped[int]         = mapped_column(Integer, primary_key=True, index=True)
    category: Mapped[str]   = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Numeric pricing fields used by the AI estimator
    base_price: Mapped[float]    = mapped_column(Float, default=0.0, nullable=False)
    per_kg_rate: Mapped[float]   = mapped_column(Float, default=0.0, nullable=False)
    premium_rate: Mapped[float]  = mapped_column(Float, default=0.0, nullable=False)

    # Condition multipliers  (1.0 = 100% of base)
    condition_multiplier_working: Mapped[float]  = mapped_column(Float, default=1.0)
    condition_multiplier_partial: Mapped[float]  = mapped_column(Float, default=0.6)
    condition_multiplier_broken: Mapped[float]   = mapped_column(Float, default=0.3)

    min_weight: Mapped[float] = mapped_column(Float, default=0.0)
    unit: Mapped[str]         = mapped_column(String(20), default="kg")
    active: Mapped[bool]      = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


# ─────────────────────────────────────────────────────────────────────────────
#  PickupReview  (user rating on a completed pickup)
# ─────────────────────────────────────────────────────────────────────────────
class PickupReview(Base):
    __tablename__ = "pickup_reviews"

    id: Mapped[int]         = mapped_column(Integer, primary_key=True, index=True)
    pickup_id: Mapped[int]  = mapped_column(Integer, ForeignKey("pickup_requests.id"), nullable=False)
    user_id: Mapped[int]    = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    rating: Mapped[int]     = mapped_column(Integer, nullable=False)   # 1-5
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    pickup = relationship("PickupRequest")
    user   = relationship("User")


# ─────────────────────────────────────────────────────────────────────────────
#  Notification
# ─────────────────────────────────────────────────────────────────────────────
class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int]         = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int]    = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    title: Mapped[str]      = mapped_column(String(200), nullable=False)
    message: Mapped[str]    = mapped_column(Text, nullable=False)
    is_read: Mapped[bool]   = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User")
