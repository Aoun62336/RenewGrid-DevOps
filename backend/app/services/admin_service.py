"""
services/admin_service.py — Business logic for admin actions.
"""
from typing import List, Tuple, Dict, Any, Optional
from fastapi import BackgroundTasks, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.core import PickupRequest, PickupStatus
from app.models.waste import WasteUpload
from app.schemas.admin import AssignPickupIn, CreateUserIn, RecyclerStatusIn
from app.core.security import hash_password
from app.repositories.user_repository import user_repo
from app.repositories.pickup_repository import pickup_repo
from app.repositories.waste_repository import waste_repo

def dashboard_overview(db: Session) -> Dict[str, Any]:
    total_users       = db.query(User).filter(User.role == UserRole.USER).count()
    active_users      = db.query(User).filter(User.role == UserRole.USER, User.is_active == True).count()
    suspended_users   = total_users - active_users
    total_waste       = waste_repo.get_total_count(db)
    total_pickups     = pickup_repo.get_total_count(db)
    completed_pickups = pickup_repo.get_completed_count(db)
    active_collectors = user_repo.get_active_count_by_role(db, UserRole.COLLECTOR)
    active_recyclers  = user_repo.get_active_count_by_role(db, UserRole.RECYCLER)

    return {
        "total_users": total_users,
        "active_users": active_users,
        "suspended_users": suspended_users,
        "total_waste_uploaded": total_waste,
        "total_pickups": total_pickups,
        "completed_pickups": completed_pickups,
        "active_collectors": active_collectors,
        "active_recyclers": active_recyclers,
    }

def list_users(db: Session, page: int, page_size: int, role: Optional[UserRole], is_active: Optional[bool], search: Optional[str] = None) -> Tuple[int, List[User]]:
    return user_repo.get_paginated(db, page, page_size, role, is_active, search=search)

def block_user(db: Session, user_id: int) -> Dict[str, str]:
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.is_active = False
    db.commit()
    return {"message": f"User {user.email} has been blocked."}

def unblock_user(db: Session, user_id: int) -> Dict[str, str]:
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user.is_active = True
    db.commit()
    return {"message": f"User {user.email} has been unblocked."}

def list_all_pickups(db: Session, page: int, page_size: int, status: Optional[PickupStatus]) -> Tuple[int, List[PickupRequest]]:
    return pickup_repo.get_all_paginated(db, page, page_size, status)

def list_all_waste(db: Session, page: int, page_size: int) -> Tuple[int, List[WasteUpload]]:
    return waste_repo.get_all_paginated(db, page, page_size)

def get_reports(db: Session) -> Dict[str, Any]:
    total_weight = db.query(func.sum(PickupRequest.final_collected_weight)).scalar() or 0.0
    by_status = (
        db.query(PickupRequest.status, func.count(PickupRequest.id))
        .group_by(PickupRequest.status)
        .all()
    )
    return {
        "total_waste_collected_kg": round(total_weight, 2),
        "pickups_by_status": {s.value: c for s, c in by_status},
    }

from app.services.event_service import handle_pickup_assigned

def assign_pickup(db: Session, pickup_id: int, body: AssignPickupIn, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    pickup = pickup_repo.get_by_id(db, pickup_id)
    if not pickup:
        raise HTTPException(status_code=404, detail="Pickup not found.")

    collector = user_repo.get_active_collector(db, body.collector_id)
    if not collector:
        raise HTTPException(status_code=404, detail="Active collector not found.")
    if not getattr(collector, 'is_available', True):
        raise HTTPException(status_code=400, detail="Collector is not available for new assignments.")

    recycler = None
    if body.recycler_id:
        # Check if the user exists and is a recycler
        recycler = user_repo.get_by_id_and_role(db, body.recycler_id, UserRole.RECYCLER)
        if not recycler or not recycler.is_active:
            raise HTTPException(status_code=404, detail="Active recycler not found.")
        pickup.recycler_id = body.recycler_id

    pickup.collector_id = body.collector_id
    pickup.status = PickupStatus.ASSIGNED

    db.commit()
    db.refresh(pickup)
    
    # Trigger event
    handle_pickup_assigned(background_tasks, pickup, collector)
    
    msg = f"Pickup #{pickup_id} assigned to collector '{collector.full_name}'"
    if recycler:
        msg += f" and recycler '{recycler.full_name}'"
    msg += "."

    return {
        "message": msg,
        "pickup_id": pickup_id,
        "collector_id": body.collector_id,
        "recycler_id": body.recycler_id,
        "status": pickup.status
    }

def create_user(db: Session, body: CreateUserIn) -> Dict[str, Any]:
    role_map = {"user": UserRole.USER, "collector": UserRole.COLLECTOR, "recycler": UserRole.RECYCLER}
    if body.role not in role_map:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {list(role_map.keys())}")

    existing = user_repo.get_by_email(db, body.email)
    if existing:
        raise HTTPException(status_code=409, detail="A user with this email already exists.")

    user = user_repo.create(
        db=db,
        full_name=body.full_name,
        email=body.email,
        password_hash=hash_password(body.password),
        role=role_map[body.role]
    )
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully.", "user_id": user.id, "email": user.email, "role": user.role}

def update_user(db: Session, user_id: int, body: Any) -> Dict[str, Any]:
    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if body.full_name is not None:
        user.full_name = body.full_name
    if body.email is not None:
        # Check if new email is taken by someone else
        existing = user_repo.get_by_email(db, body.email)
        if existing and existing.id != user_id:
            raise HTTPException(status_code=409, detail="A user with this email already exists.")
        user.email = body.email
    if body.role is not None:
        role_map = {"user": UserRole.USER, "collector": UserRole.COLLECTOR, "recycler": UserRole.RECYCLER}
        role_val = body.role.lower()
        if role_val not in role_map:
            raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {list(role_map.keys())}")
        user.role = role_map[role_val]

    db.commit()
    db.refresh(user)
    return {"message": "User updated successfully.", "user_id": user.id}

def approve_recycler(db: Session, user_id: int, body: RecyclerStatusIn) -> Dict[str, Any]:
    if body.status not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Status must be 'approved' or 'rejected'.")

    user = user_repo.get_by_id_and_role(db, user_id, UserRole.RECYCLER)
    if not user:
        raise HTTPException(status_code=404, detail="Recycler not found.")

    if body.status == "approved":
        user.is_active = True
        db.commit()
        return {"message": f"Recycler '{user.full_name}' has been approved.", "user_id": user_id, "status": "approved"}
    else:
        # Hard-delete rejected recyclers so they cannot login or appear in lists
        email = user.email
        name = user.full_name
        db.delete(user)
        db.commit()
        return {"message": f"Recycler '{name}' has been rejected and removed from the system.", "user_id": user_id, "status": "rejected"}

def delete_user(db: Session, admin: User, user_id: int) -> Dict[str, Any]:
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Admins cannot delete their own account.")

    user = user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user.role.value == "admin":
        raise HTTPException(status_code=403, detail="Cannot delete admin accounts.")

    db.delete(user)
    db.commit()
    return {"message": f"User '{user.email}' has been permanently deleted.", "user_id": user_id}


# ─── Analytics ────────────────────────────────────────────────────────────────
def get_analytics(db: Session) -> Dict[str, Any]:
    from datetime import datetime, timezone, timedelta
    from sqlalchemy import func, cast, Date, extract
    from app.models.core import Reward, PickupRequest, PickupStatus
    from app.models.waste import WasteUpload, WasteCategory

    # total CO2
    total_co2 = db.query(func.sum(Reward.co2_saved_kg)).scalar() or 0.0

    # total waste collected (completed pickups)
    total_waste_kg = (
        db.query(func.sum(PickupRequest.final_collected_weight))
        .filter(PickupRequest.status == PickupStatus.COMPLETED)
        .scalar() or 0.0
    )

    # pickups grouped by status
    by_status_rows = (
        db.query(PickupRequest.status, func.count(PickupRequest.id))
        .group_by(PickupRequest.status)
        .all()
    )
    pickups_by_status = {s.value: c for s, c in by_status_rows}

    # waste grouped by category
    by_cat_rows = (
        db.query(WasteUpload.category, func.count(WasteUpload.id))
        .group_by(WasteUpload.category)
        .all()
    )
    waste_by_category = {c.value if hasattr(c, 'value') else str(c): cnt for c, cnt in by_cat_rows}

    # pickups created today
    today = datetime.now(timezone.utc).date()
    pickups_today = (
        db.query(func.count(PickupRequest.id))
        .filter(func.date(PickupRequest.created_at) == today)
        .scalar() or 0
    )

    # pickups by month for last 12 months
    monthly_pickups_rows = (
        db.query(
            extract('year', PickupRequest.created_at).label('year'),
            extract('month', PickupRequest.created_at).label('month'),
            func.count(PickupRequest.id).label('cnt'),
        )
        .group_by('year', 'month')
        .order_by('year', 'month')
        .limit(12)
        .all()
    )
    pickups_by_month = [
        {"month": f"{int(r.year)}-{int(r.month):02d}", "count": r.cnt}
        for r in monthly_pickups_rows
    ]
    if not pickups_by_month:
        current_date = datetime.now(timezone.utc)
        for i in range(5, -1, -1):
            m_date = current_date - timedelta(days=i*30)
            pickups_by_month.append({
                "month": m_date.strftime("%Y-%m"),
                "count": 0
            })

    # total pickups
    total_pickups = pickup_repo.get_total_count(db)

    # 1. CO2 saved by Category (joined via WasteUpload -> PickupRequest -> Reward)
    co2_by_cat_rows = (
        db.query(WasteUpload.category, func.sum(Reward.co2_saved_kg))
        .join(PickupRequest, PickupRequest.waste_upload_id == WasteUpload.id)
        .join(Reward, Reward.pickup_id == PickupRequest.id)
        .group_by(WasteUpload.category)
        .all()
    )
    co2_by_category = {cat.value: 0.0 for cat in WasteCategory}
    for c, val in co2_by_cat_rows:
        cat_key = c.value if hasattr(c, 'value') else str(c)
        co2_by_category[cat_key] = round(float(val or 0.0), 2)

    # 2. CO2 saved by month for last 12 months
    co2_by_month_rows = (
        db.query(
            extract('year', Reward.created_at).label('year'),
            extract('month', Reward.created_at).label('month'),
            func.sum(Reward.co2_saved_kg).label('co2_sum')
        )
        .group_by('year', 'month')
        .order_by('year', 'month')
        .limit(12)
        .all()
    )
    co2_by_month = [
        {"month": f"{int(r.year)}-{int(r.month):02d}", "co2": round(float(r.co2_sum or 0.0), 2)}
        for r in co2_by_month_rows
    ]
    if not co2_by_month:
        current_date = datetime.now(timezone.utc)
        for i in range(5, -1, -1):
            m_date = current_date - timedelta(days=i*30)
            co2_by_month.append({
                "month": m_date.strftime("%Y-%m"),
                "co2": 0.0
            })

    # 3. Landfill Diversion Rate (completed and recycled status pickups over total pickups)
    if total_pickups > 0:
        diverted_pickups = (
            db.query(func.count(PickupRequest.id))
            .filter(PickupRequest.status.in_([PickupStatus.COMPLETED, PickupStatus.RECYCLED]))
            .scalar() or 0
        )
        landfill_diversion_rate = round((diverted_pickups / total_pickups) * 100, 1)
    else:
        landfill_diversion_rate = 0.0

    # 4. Energy saved in kWh (multiplier: 2.5 kWh per kg of CO2 offset)
    energy_saved_kwh = round(total_co2 * 2.5, 2)

    return {
        "total_co2_saved_kg": round(total_co2, 2),
        "total_waste_collected_kg": round(total_waste_kg, 2),
        "pickups_by_status": pickups_by_status,
        "waste_by_category": waste_by_category,
        "total_pickups": total_pickups,
        "pickups_today": pickups_today,
        "pickups_by_month": pickups_by_month,
        "co2_by_category": co2_by_category,
        "co2_by_month": co2_by_month,
        "landfill_diversion_rate": landfill_diversion_rate,
        "energy_saved_kwh": energy_saved_kwh,
        "top_areas": [],
    }


# ─── Revenue ──────────────────────────────────────────────────────────────────
def get_revenue(db: Session) -> Dict[str, Any]:
    from datetime import datetime, timezone
    from sqlalchemy import func, extract
    from app.models.core import Reward, RecyclerPayment

    total_revenue = db.query(func.sum(RecyclerPayment.amount)).scalar() or 0.0

    now = datetime.now(timezone.utc)
    this_month_revenue = (
        db.query(func.sum(RecyclerPayment.amount))
        .filter(
            extract('year', RecyclerPayment.created_at) == now.year,
            extract('month', RecyclerPayment.created_at) == now.month,
        )
        .scalar() or 0.0
    )
    this_month_revenue = round(this_month_revenue, 2)
    total_revenue = round(total_revenue, 2)

    total_rewards = db.query(func.count(Reward.id)).scalar() or 0

    # revenue by month for last 12 months
    monthly_rows = (
        db.query(
            extract('year', RecyclerPayment.created_at).label('year'),
            extract('month', RecyclerPayment.created_at).label('month'),
            func.sum(RecyclerPayment.amount).label('rev'),
        )
        .group_by('year', 'month')
        .order_by('year', 'month')
        .limit(12)
        .all()
    )
    revenue_by_month = [
        {"month": f"{int(r.year)}-{int(r.month):02d}", "revenue": round(r.rev, 2)}
        for r in monthly_rows
    ]

    return {
        "total_revenue": total_revenue,
        "this_month_revenue": this_month_revenue,
        "total_rewards_issued": total_rewards,
        "revenue_by_month": revenue_by_month,
    }


# ─── Typed Reports ────────────────────────────────────────────────────────────
def get_report_by_type(db: Session, report_type: str) -> Dict[str, Any]:
    base = get_reports(db)
    analytics = get_analytics(db)
    revenue = get_revenue(db)
    from datetime import datetime, timezone
    now_str = datetime.now(timezone.utc).strftime('%B %Y')

    reports: Dict[str, Any] = {
        "monthly_summary": {**base, **analytics, "period": now_str, "type": "Monthly Summary"},
        "compliance":      {"status": "Compliant", "certifications": ["ISO 14001", "R2v3"], "period": now_str, "type": "Compliance"},
        "financial":       {**revenue, "period": now_str, "type": "Financial"},
        "environmental":   {"total_co2_saved_kg": analytics["total_co2_saved_kg"],
                            "trees_equivalent": round(analytics["total_co2_saved_kg"] / 20, 1),
                            "period": now_str, "type": "Environmental Impact"},
        "collector_performance": base,
        "waste_audit":     {"waste_by_category": analytics["waste_by_category"],
                            "total_waste_kg": analytics["total_waste_collected_kg"],
                            "period": now_str, "type": "Waste Audit"},
    }
    from fastapi import HTTPException as _HTTPException
    if report_type not in reports:
        raise _HTTPException(status_code=404, detail=f"Unknown report type '{report_type}'.")
    return reports[report_type]


# ─── Pricing Rules ────────────────────────────────────────────────────────────
def _serialize_rule(r) -> Dict[str, Any]:
    return {
        "id": r.id,
        "category": r.category,
        "description": r.description,
        "base_price": r.base_price,
        "per_kg_rate": r.per_kg_rate,
        "premium_rate": r.premium_rate,
        "condition_multiplier_working": r.condition_multiplier_working,
        "condition_multiplier_partial": r.condition_multiplier_partial,
        "condition_multiplier_broken": r.condition_multiplier_broken,
        "min_weight": r.min_weight,
        "unit": r.unit,
        "active": r.active,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
    }

def list_pricing_rules(db: Session) -> list[Dict[str, Any]]:
    from app.models.core import PricingRule
    rules = db.query(PricingRule).order_by(PricingRule.category).all()
    if not rules:
        # Seed defaults matching WasteCategory values
        defaults = [
            PricingRule(category='Laptops & Computers', description='Laptops, desktops, servers',
                        base_price=8000.0, per_kg_rate=500.0, premium_rate=1000.0,
                        condition_multiplier_working=1.0, condition_multiplier_partial=0.6, condition_multiplier_broken=0.3,
                        min_weight=0.5, unit='kg', active=True),
            PricingRule(category='Mobile Phones', description='Smartphones, feature phones, tablets',
                        base_price=6500.0, per_kg_rate=500.0, premium_rate=1500.0,
                        condition_multiplier_working=1.0, condition_multiplier_partial=0.5, condition_multiplier_broken=0.25,
                        min_weight=0.1, unit='kg', active=True),
            PricingRule(category='Circuit Boards', description='PCBs, motherboards, GPUs, RAM modules',
                        base_price=1000.0, per_kg_rate=1500.0, premium_rate=2000.0,
                        condition_multiplier_working=1.0, condition_multiplier_partial=0.7, condition_multiplier_broken=0.4,
                        min_weight=0.2, unit='kg', active=True),
            PricingRule(category='Batteries', description='Li-ion, NiMH, lead-acid batteries',
                        base_price=300.0, per_kg_rate=250.0, premium_rate=500.0,
                        condition_multiplier_working=1.0, condition_multiplier_partial=0.5, condition_multiplier_broken=0.2,
                        min_weight=0.1, unit='kg', active=True),
            PricingRule(category='Monitors & Displays', description='LCD, LED, CRT monitors',
                        base_price=1200.0, per_kg_rate=150.0, premium_rate=300.0,
                        condition_multiplier_working=1.0, condition_multiplier_partial=0.5, condition_multiplier_broken=0.2,
                        min_weight=1.0, unit='kg', active=True),
            PricingRule(category='Printers & Peripherals', description='Printers, scanners, keyboards, mice',
                        base_price=800.0, per_kg_rate=100.0, premium_rate=250.0,
                        condition_multiplier_working=1.0, condition_multiplier_partial=0.5, condition_multiplier_broken=0.2,
                        min_weight=0.5, unit='kg', active=True),
            PricingRule(category='Mixed Electronics', description='Assorted electronic waste',
                        base_price=400.0, per_kg_rate=150.0, premium_rate=200.0,
                        condition_multiplier_working=1.0, condition_multiplier_partial=0.5, condition_multiplier_broken=0.2,
                        min_weight=0.5, unit='kg', active=True),
        ]
        db.add_all(defaults)
        db.commit()
        rules = db.query(PricingRule).order_by(PricingRule.category).all()

    return [_serialize_rule(r) for r in rules]

def create_pricing_rule(db: Session, body: dict) -> Dict[str, Any]:
    from app.models.core import PricingRule
    rule = PricingRule(
        category=body.get('category', 'Unknown'),
        description=body.get('description', ''),
        base_price=float(body.get('base_price', 0)),
        per_kg_rate=float(body.get('per_kg_rate', 0)),
        premium_rate=float(body.get('premium_rate', 0)),
        condition_multiplier_working=float(body.get('condition_multiplier_working', 1.0)),
        condition_multiplier_partial=float(body.get('condition_multiplier_partial', 0.6)),
        condition_multiplier_broken=float(body.get('condition_multiplier_broken', 0.3)),
        min_weight=float(body.get('min_weight', 0)),
        unit=body.get('unit', 'kg'),
        active=body.get('active', True),
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return {**_serialize_rule(rule), "message": "Rule created successfully."}

def update_pricing_rule(db: Session, rule_id: int, body: dict) -> Dict[str, Any]:
    from app.models.core import PricingRule
    from fastapi import HTTPException
    rule = db.query(PricingRule).filter(PricingRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for field in ['category', 'description', 'unit']:
        if field in body:
            setattr(rule, field, body[field])
    for field in ['base_price', 'per_kg_rate', 'premium_rate',
                   'condition_multiplier_working', 'condition_multiplier_partial',
                   'condition_multiplier_broken', 'min_weight']:
        if field in body:
            setattr(rule, field, float(body[field]))
    if 'active' in body:
        rule.active = body['active']
    db.commit()
    db.refresh(rule)
    return {**_serialize_rule(rule), "message": "Rule updated successfully."}

def delete_pricing_rule(db: Session, rule_id: int) -> Dict[str, Any]:
    from app.models.core import PricingRule
    from fastapi import HTTPException
    rule = db.query(PricingRule).filter(PricingRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return {"message": "Rule deleted successfully."}


# ─── Trend Forecasting ────────────────────────────────────────────────────────
def get_forecast(db: Session) -> Dict[str, Any]:
    from datetime import datetime, timezone, timedelta
    from sqlalchemy import func, extract
    from app.models.core import PickupRequest

    now = datetime.now(timezone.utc)
    six_months_ago = now - timedelta(days=182)

    rows = (
        db.query(
            extract('year', PickupRequest.created_at).label('y'),
            extract('month', PickupRequest.created_at).label('m'),
            func.count(PickupRequest.id).label('cnt')
        )
        .filter(PickupRequest.created_at >= six_months_ago)
        .group_by('y', 'm')
        .order_by('y', 'm')
        .all()
    )

    # Fallback if not enough data
    if len(rows) < 2:
        base = rows[0].cnt if rows else 10
        return {
            "next_month_forecast_pct_change": "+15%",
            "peak_month": "Dec",
            "recommended_additional_collectors": "+4",
            "forecast_data": [
                {"month": f"Month {i+1}", "predicted": max(1, base + i * 2)}
                for i in range(6)
            ]
        }

    import calendar
    peak_row = max(rows, key=lambda x: x.cnt)
    peak_month = calendar.month_name[int(peak_row.m)]

    counts = [r.cnt for r in rows]
    growths = [(counts[i] - counts[i-1]) / max(1, counts[i-1]) for i in range(1, len(counts))]
    avg_growth = sum(growths) / len(growths) if growths else 0.0

    next_month_change = f"{'+' if avg_growth >= 0 else ''}{round(avg_growth * 100)}%"

    # Build forecast for next 6 months
    last_count = counts[-1]
    forecast_data = []
    for i in range(1, 7):
        predicted = max(1, round(last_count * ((1 + avg_growth) ** i)))
        month_idx = (int(rows[-1].m) + i - 1) % 12 + 1
        forecast_data.append({"month": calendar.month_abbr[month_idx], "predicted": predicted})

    return {
        "next_month_forecast_pct_change": next_month_change,
        "peak_month": peak_month,
        "recommended_additional_collectors": f"+{max(1, round(last_count * avg_growth / 20))}",
        "forecast_data": forecast_data,
        "historical_data": [{"month": f"{calendar.month_abbr[int(r.m)]} {int(r.y)}", "count": r.cnt} for r in rows],
    }


# ─── Payments (Revenue Tracking) ──────────────────────────────────────────────
def list_payments(db, page, page_size):
    from app.models.core import RecyclerPayment
    from sqlalchemy import func
    q = db.query(RecyclerPayment).order_by(RecyclerPayment.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    total_amount = db.query(func.sum(RecyclerPayment.amount)).scalar() or 0.0
    return {
        "total": total,
        "total_amount": round(total_amount, 2),
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": p.id,
                "pickup_id": p.pickup_id,
                "user_name": p.user.full_name if p.user else f"User #{p.user_id}",
                "user_id": p.user_id,
                "recycler_name": p.recycler.full_name if p.recycler else f"Recycler #{p.recycler_id}",
                "recycler_id": p.recycler_id,
                "waste_item": p.waste_item or "E-Waste",
                "amount": p.amount,
                "note": p.note,
                "date": p.created_at.isoformat(),
            }
            for p in items
        ],
    }


# ─── Completed Jobs for Reward Assignment ─────────────────────────────────────
def list_completed_jobs(db, page, page_size):
    from app.models.core import PickupRequest, PickupStatus, Reward
    q = (
        db.query(PickupRequest)
        .filter(PickupRequest.status == PickupStatus.COMPLETED)
        .order_by(PickupRequest.updated_at.desc())
    )
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    pickup_ids = [p.id for p in items]
    rewarded = set(
        r.pickup_id for r in db.query(Reward.pickup_id).filter(Reward.pickup_id.in_(pickup_ids)).all()
    ) if pickup_ids else set()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "pickup_id": p.id,
                "user_id": p.user_id,
                "user_name": p.user.full_name if p.user else f"User #{p.user_id}",
                "waste_item": p.waste.title if p.waste else f"Pickup #{p.id}",
                "category": p.waste.category if p.waste else "N/A",
                "weight_kg": p.final_collected_weight,
                "final_price": p.final_price,
                "completed_at": p.updated_at.isoformat() if p.updated_at else None,
                "reward_assigned": p.id in rewarded,
                "estimated_credit_points": p.waste.estimated_credit_points if p.waste else None,
                "estimated_co2_saved": p.waste.estimated_co2_saved if p.waste else None,
            }
            for p in items
        ],
    }


# ─── Assign Reward Points (Admin) ─────────────────────────────────────────────
def assign_reward_points(db, pickup_id, user_id, points, co2_saved_kg=0.0):
    from app.models.core import Reward, Notification
    from fastapi import HTTPException
    if points <= 0:
        raise HTTPException(status_code=400, detail="Points must be positive.")
    existing = db.query(Reward).filter(Reward.pickup_id == pickup_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Reward already assigned for this pickup.")
    reward = Reward(user_id=user_id, pickup_id=pickup_id, points=points, co2_saved_kg=co2_saved_kg)
    db.add(reward)
    notif = Notification(
        user_id=user_id,
        title="Reward Points Assigned",
        message=f"Admin awarded {points} points for pickup #{pickup_id}! CO2 saved: {co2_saved_kg} kg.",
    )
    db.add(notif)
    db.commit()
    db.refresh(reward)
    return {
        "message": f"Reward of {points} pts assigned to user #{user_id} for pickup #{pickup_id}.",
        "reward_id": reward.id,
        "points": points,
        "co2_saved_kg": co2_saved_kg,
    }
