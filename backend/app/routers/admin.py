"""
routers/admin.py — Admin dashboard and management endpoints.
Role guard: only ADMIN role can access these routes.
"""
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.models.user import User, UserRole
from app.models.core import PickupStatus
from app.schemas.auth import UserPublic
from app.schemas.admin import AssignPickupIn, CreateUserIn, RecyclerStatusIn, UpdateUserIn
from app.services import admin_service

router = APIRouter()

# ─── GET /admin/dashboard/overview ───────────────────────────────────────────
@router.get("/dashboard/overview", summary="Aggregated platform metrics")
def dashboard_overview(
    db: Session = Depends(get_db),
    _: User     = Depends(require_role(UserRole.ADMIN)),
):
    return admin_service.dashboard_overview(db)

# ─── GET /admin/analytics ────────────────────────────────────────────────────
@router.get("/analytics", summary="Platform analytics: CO2, waste, pickups, areas")
def get_analytics(
    db: Session = Depends(get_db),
    _: User     = Depends(require_role(UserRole.ADMIN)),
):
    return admin_service.get_analytics(db)

# ─── GET /admin/revenue ───────────────────────────────────────────────────────
@router.get("/revenue", summary="Revenue tracking: total, monthly, per-reward")
def get_revenue(
    db: Session = Depends(get_db),
    _: User     = Depends(require_role(UserRole.ADMIN)),
):
    return admin_service.get_revenue(db)

# ─── GET /admin/users ─────────────────────────────────────────────────────────
@router.get("/users", response_model=dict, summary="Paginated user list with filters")
def list_users(
    page: int          = Query(1, ge=1),
    page_size: int     = Query(20, ge=1, le=100),
    role: Optional[UserRole] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None, description="Filter by full_name or email (case-insensitive LIKE)"),
    db: Session        = Depends(get_db),
    _: User            = Depends(require_role(UserRole.ADMIN)),
):
    total, items = admin_service.list_users(db, page, page_size, role, is_active, search=search)
    return {"total": total, "page": page, "page_size": page_size,
            "items": [UserPublic.model_validate(u) for u in items]}

# ─── PUT /admin/block-user/{user_id} ─────────────────────────────────────────
@router.put("/block-user/{user_id}", summary="Block a user (set is_active=false)")
def block_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User     = Depends(require_role(UserRole.ADMIN)),
):
    return admin_service.block_user(db, user_id)

# ─── PUT /admin/unblock-user/{user_id} ───────────────────────────────────────
@router.put("/unblock-user/{user_id}", summary="Unblock a user (set is_active=true)")
def unblock_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User     = Depends(require_role(UserRole.ADMIN)),
):
    return admin_service.unblock_user(db, user_id)

# ─── GET /admin/pickups ───────────────────────────────────────────────────────
@router.get("/pickups", response_model=dict, summary="All pickups with filters")
def list_all_pickups(
    page: int      = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[PickupStatus] = Query(None),
    db: Session    = Depends(get_db),
    _: User        = Depends(require_role(UserRole.ADMIN)),
):
    total, items = admin_service.list_all_pickups(db, page, page_size, status)
    from app.schemas.pickup import PickupResponse
    return {"total": total, "page": page, "page_size": page_size,
            "items": [PickupResponse.model_validate(i) for i in items]}

# ─── GET /admin/waste-uploads ─────────────────────────────────────────────────
@router.get("/waste-uploads", response_model=dict, summary="All waste uploads")
def list_all_waste(
    page: int      = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session    = Depends(get_db),
    _: User        = Depends(require_role(UserRole.ADMIN)),
):
    total, items = admin_service.list_all_waste(db, page, page_size)
    from app.schemas.waste import WasteUploadResponse
    return {"total": total, "page": page, "page_size": page_size,
            "items": [WasteUploadResponse.model_validate(i) for i in items]}

# ─── GET /admin/reports ───────────────────────────────────────────────────────
@router.get("/reports", summary="Operational summary report")
def get_reports(
    db: Session = Depends(get_db),
    _: User     = Depends(require_role(UserRole.ADMIN)),
):
    return admin_service.get_reports(db)

# ─── GET /admin/reports/{report_type} ────────────────────────────────────────
@router.get("/reports/{report_type}", summary="Download a named report as JSON or CSV")
def download_report(
    report_type: str,
    format: str = Query("json", description="json or csv"),
    db: Session = Depends(get_db),
    _: User     = Depends(require_role(UserRole.ADMIN)),
):
    data = admin_service.get_report_by_type(db, report_type)
    if format == "csv":
        from fastapi.responses import StreamingResponse
        import io, csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        def flatten_dict(d, parent_key='', sep='_'):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                elif isinstance(v, list):
                    items.append((new_key, str(v)))
                else:
                    items.append((new_key, v))
            return dict(items)
            
        flat_data = flatten_dict(data)
        writer.writerow(flat_data.keys())
        writer.writerow(flat_data.values())
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={report_type}.csv"}
        )
    return data

from pydantic import BaseModel
class BroadcastIn(BaseModel):
    message: str
    level: str = "info"

@router.post("/broadcast", summary="Broadcast notification to all users")
def broadcast_message(
    body: BroadcastIn,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: User     = Depends(require_role(UserRole.ADMIN)),
):
    # Mocking broadcast since we don't have a real broadcast service yet
    # We would insert Notifications for all users here
    return {"message": "Broadcast sent successfully", "content": body.message}

# ─── PUT /admin/assign-pickup/{pickup_id} ────────────────────────────────────
@router.put("/assign-pickup/{pickup_id}", summary="Assign a collector to a pickup")
def assign_pickup(
    pickup_id: int,
    body: AssignPickupIn,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: User     = Depends(require_role(UserRole.ADMIN)),
):
    return admin_service.assign_pickup(db, pickup_id, body, background_tasks)

# ─── POST /admin/create-user ──────────────────────────────────────────────────
@router.post("/create-user", status_code=201, summary="Admin creates a user directly")
def admin_create_user(
    body: CreateUserIn,
    db: Session = Depends(get_db),
    _: User     = Depends(require_role(UserRole.ADMIN)),
):
    return admin_service.create_user(db, body)

# ─── PUT /admin/update-user/{user_id} ────────────────────────────────────────
@router.put("/update-user/{user_id}", summary="Admin edits a user's details")
def admin_update_user(
    user_id: int,
    body: UpdateUserIn,
    db: Session = Depends(get_db),
    _: User     = Depends(require_role(UserRole.ADMIN)),
):
    return admin_service.update_user(db, user_id, body)

# ─── PUT /admin/approve-recycler/{user_id} ───────────────────────────────────
@router.put("/approve-recycler/{user_id}", summary="Approve or reject a recycler")
def approve_recycler(
    user_id: int,
    body: RecyclerStatusIn,
    db: Session = Depends(get_db),
    _: User     = Depends(require_role(UserRole.ADMIN)),
):
    return admin_service.approve_recycler(db, user_id, body)

# ─── DELETE /admin/delete-user/{user_id} ─────────────────────────────────────
@router.delete("/delete-user/{user_id}", summary="Soft-delete a user (deactivate)")
def delete_user(
    user_id: int,
    db: Session  = Depends(get_db),
    admin: User  = Depends(require_role(UserRole.ADMIN)),
):
    return admin_service.delete_user(db, admin, user_id)

# ─── PATCH /admin/recyclers/{user_id}/status ─────────────────────────────────
@router.patch("/recyclers/{user_id}/status", summary="Approve or reject a recycler (PATCH alias)")
def patch_recycler_status(
    user_id: int,
    body: RecyclerStatusIn,
    db: Session = Depends(get_db),
    _: User     = Depends(require_role(UserRole.ADMIN)),
):
    return admin_service.approve_recycler(db, user_id, body)

# ─── Pricing Rules CRUD ───────────────────────────────────────────────────────
@router.get("/pricing-rules", summary="List all pricing rules")
def list_pricing_rules(
    db: Session = Depends(get_db),
    _: User     = Depends(require_role(UserRole.ADMIN)),
):
    return admin_service.list_pricing_rules(db)

@router.post("/pricing-rules", status_code=201, summary="Create a pricing rule")
def create_pricing_rule(
    body: dict,
    db: Session = Depends(get_db),
    _: User     = Depends(require_role(UserRole.ADMIN)),
):
    return admin_service.create_pricing_rule(db, body)

@router.put("/pricing-rules/{rule_id}", summary="Update a pricing rule")
def update_pricing_rule(
    rule_id: int,
    body: dict,
    db: Session = Depends(get_db),
    _: User     = Depends(require_role(UserRole.ADMIN)),
):
    return admin_service.update_pricing_rule(db, rule_id, body)

@router.delete("/pricing-rules/{rule_id}", summary="Delete a pricing rule")
def delete_pricing_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    _: User     = Depends(require_role(UserRole.ADMIN)),
):
    return admin_service.delete_pricing_rule(db, rule_id)

# ─── GET /admin/forecast ──────────────────────────────────────────────────────
@router.get("/forecast", summary="Linear regression forecast for next month pickup volume")
def get_forecast(
    db: Session = Depends(get_db),
    _: User     = Depends(require_role(UserRole.ADMIN)),
):
    return admin_service.get_forecast(db)

# ─── POST /recycler/ai-recommend/{pickup_id} (admin-visible proxy) ────────────
@router.get("/ai-recommend/{pickup_id}", summary="Rule-based AI recommendation for a pickup")
def ai_recommend(
    pickup_id: int,
    db: Session = Depends(get_db),
    _: User     = Depends(require_role(UserRole.ADMIN)),
):
    from app.services import recycler_service
    return recycler_service.get_ai_recommendation(db, pickup_id)


# ─── GET /admin/payments ───────────────────────────────────────────────────────
@router.get("/payments", summary="All recycler-to-user payments (Revenue Tracking)")
def list_payments(
    page: int      = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session    = Depends(get_db),
    _: User        = Depends(require_role(UserRole.ADMIN)),
):
    return admin_service.list_payments(db, page, page_size)


# ─── GET /admin/completed-jobs ────────────────────────────────────────────────
@router.get("/completed-jobs", summary="Completed recycling jobs for reward point assignment")
def list_completed_jobs(
    page: int      = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session    = Depends(get_db),
    _: User        = Depends(require_role(UserRole.ADMIN)),
):
    return admin_service.list_completed_jobs(db, page, page_size)


# ─── POST /admin/assign-reward-points ────────────────────────────────────────
from pydantic import BaseModel as _BaseModel
class AssignRewardIn(_BaseModel):
    pickup_id: int
    user_id: int
    points: int
    co2_saved_kg: float = 0.0

@router.post("/assign-reward-points", status_code=201, summary="Admin assigns reward points to user for a completed job")
def assign_reward_points(
    body: AssignRewardIn,
    db: Session = Depends(get_db),
    _: User     = Depends(require_role(UserRole.ADMIN)),
):
    return admin_service.assign_reward_points(db, body.pickup_id, body.user_id, body.points, body.co2_saved_kg)
