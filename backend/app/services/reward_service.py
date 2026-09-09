"""
services/reward_service.py — Reward generation logic.

Called as a FastAPI BackgroundTask when a pickup reaches COMPLETED status.
Idempotent: silently no-ops if a reward already exists for the pickup.

Configurable multipliers (override via AppConfig rows if needed):
  POINTS_PER_KG  = 10   → points  = weight_kg * 10
  CO2_PER_KG     = 0.5  → co2_kg  = weight_kg * 0.5
"""
import logging
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.core import PickupRequest, Reward, Notification

logger = logging.getLogger(__name__)

# ── Configurable multipliers ──────────────────────────────────────────────────
POINTS_PER_KG: float = 10.0   # points awarded per kg of waste collected
CO2_PER_KG: float    = 0.5    # kg of CO₂ saved per kg of waste collected


def _calculate_reward(weight_kg: float) -> tuple[int, float]:
    """Return (points, co2_saved_kg) for a given weight."""
    points    = max(0, int(weight_kg * POINTS_PER_KG))
    co2_saved = max(0.0, round(weight_kg * CO2_PER_KG, 4))
    return points, co2_saved


def create_reward_for_pickup(pickup_id: int, user_id: int, weight_kg: float) -> None:
    """
    Idempotently create a Reward row for a completed pickup.

    Designed to run inside a FastAPI BackgroundTask — opens its own DB
    session so the foreground response is never blocked.

    Args:
        pickup_id:  PK of the completed PickupRequest.
        user_id:    PK of the user who owns the pickup (reward recipient).
        weight_kg:  Final collected weight used for point calculation.
    """
    db: Session = SessionLocal()
    try:
        # ── Idempotency guard ─────────────────────────────────────────────────
        existing = db.query(Reward).filter(Reward.pickup_id == pickup_id).first()
        if existing:
            logger.info(
                "Reward already exists for pickup_id=%d (reward_id=%d) — skipping.",
                pickup_id, existing.id,
            )
            return

        # ── Guard against zero / missing weight ───────────────────────────────
        if not weight_kg or weight_kg <= 0:
            logger.warning(
                "Pickup %d has no valid weight (%.2f kg) — reward not created.",
                pickup_id, weight_kg or 0,
            )
            return

        points, co2_saved = _calculate_reward(weight_kg)

        reward = Reward(
            user_id=user_id,
            pickup_id=pickup_id,
            points=points,
            co2_saved_kg=co2_saved,
        )
        db.add(reward)

        # Notify the user
        notif = Notification(
            user_id=user_id,
            title="Reward Generated",
            message=f"You've earned {points} points and saved {co2_saved} kg of CO₂ for pickup #{pickup_id}!"
        )
        db.add(notif)

        db.commit()
        db.refresh(reward)

        logger.info(
            "Reward created: pickup_id=%d, user_id=%d, points=%d, co2_saved_kg=%.4f",
            pickup_id, user_id, points, co2_saved,
        )

    except Exception:
        db.rollback()
        logger.exception("Failed to create reward for pickup_id=%d.", pickup_id)
    finally:
        db.close()
