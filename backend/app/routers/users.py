"""
routers/users.py — User-specific endpoints.
Includes: GET /user/rewards (with Reward Points + Reward Payment sections)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.models.core import Reward, RecyclerPayment

router = APIRouter()


# ─── GET /users/rewards ───────────────────────────────────────────────────────
@router.get("/rewards", summary="Get authenticated user's reward points, wallet balance, and payment history")
def get_rewards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ── Reward Points (from auto-completion or admin assignment) ──────────────
    rewards = (
        db.query(Reward)
        .filter(Reward.user_id == current_user.id)
        .order_by(Reward.created_at.desc())
        .all()
    )

    total_points = sum(r.points for r in rewards)
    total_co2    = sum(r.co2_saved_kg for r in rewards)

    # Wallet balance: 1 point = ₹0.10
    wallet_balance = round(total_points * 0.10, 2)

    reward_history = [
        {
            "id": r.id,
            "pickup_id": r.pickup_id,
            "points": r.points,
            "co2_saved_kg": r.co2_saved_kg,
            "earned_at": r.created_at.isoformat(),
        }
        for r in rewards
    ]

    # ── Reward Payments (monetary payments from recyclers) ────────────────────
    payments = (
        db.query(RecyclerPayment)
        .filter(RecyclerPayment.user_id == current_user.id)
        .order_by(RecyclerPayment.created_at.desc())
        .all()
    )

    total_payment_received = round(sum(p.amount for p in payments), 2)

    payment_history = [
        {
            "id": p.id,
            "pickup_id": p.pickup_id,
            "amount": p.amount,
            "waste_item": p.waste_item or "E-Waste",
            "note": p.note,
            "received_at": p.created_at.isoformat(),
        }
        for p in payments
    ]

    return {
        "user_id": current_user.id,
        # Reward Points section
        "points": total_points,
        "wallet_balance": wallet_balance,
        "co2_saved_kg": round(total_co2, 2),
        "reward_history": reward_history,
        # Reward Payment section (monetary)
        "total_payment_received": total_payment_received,
        "payment_history": payment_history,
    }
