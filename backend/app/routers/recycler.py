"""
routers/recycler.py — Recycler module endpoints.
Role guard: only users with role=RECYCLER can access these.
"""
from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_role
from app.models.user import User, UserRole
from app.models.core import ProcessingRecord
from app.schemas.pickup import PickupResponse
from app.schemas.recycler import ProcessStartIn, ProcessUpdateIn, ProcessingRecordOut, InventoryItemOut
from app.services import recycler_service

router = APIRouter()

# ─── GET /recycler/assigned-waste ────────────────────────────────────────────
@router.get("/assigned-waste", response_model=dict, summary="Waste items in COLLECTED status available for processing")
def assigned_waste(
    page: int      = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session    = Depends(get_db),
    recycler: User = Depends(require_role(UserRole.RECYCLER)),
):
    total, items = recycler_service.get_assigned_waste(db, recycler, page, page_size)
    return {"total": total, "page": page, "page_size": page_size,
            "items": [PickupResponse.model_validate(i) for i in items]}

# ─── POST /recycler/process/{pickup_id} ──────────────────────────────────────
@router.post("/process/{pickup_id}", response_model=ProcessingRecordOut, status_code=201, summary="Start processing: COLLECTED → PROCESSING")
def start_processing(
    pickup_id: int,
    body: ProcessStartIn,
    db: Session    = Depends(get_db),
    recycler: User = Depends(require_role(UserRole.RECYCLER)),
):
    return recycler_service.start_processing(db, recycler, pickup_id, body)

# ─── PUT /recycler/update-status/{pickup_id} ─────────────────────────────────
@router.put("/update-status/{pickup_id}", response_model=ProcessingRecordOut, summary="Update processing outcome: RECYCLED or COMPLETED")
def update_processing(
    pickup_id: int,
    body: ProcessUpdateIn,
    background_tasks: BackgroundTasks,
    db: Session    = Depends(get_db),
    recycler: User = Depends(require_role(UserRole.RECYCLER)),
):
    return recycler_service.update_processing(db, recycler, pickup_id, body, background_tasks)

# ─── GET /recycler/inventory ──────────────────────────────────────────────────
@router.get("/inventory", response_model=dict, summary="Processed waste inventory")
def get_inventory(
    page: int      = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session    = Depends(get_db),
    recycler: User = Depends(require_role(UserRole.RECYCLER)),
):
    total, items = recycler_service.get_inventory(db, recycler, page, page_size)
    return {"total": total, "page": page, "page_size": page_size,
            "items": [InventoryItemOut.model_validate(i) for i in items]}

# ─── GET /recycler/history ────────────────────────────────────────────────────
@router.get("/history", response_model=dict, summary="Processing history for current recycler")
def processing_history(
    page: int      = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session    = Depends(get_db),
    recycler: User = Depends(require_role(UserRole.RECYCLER)),
):
    q = (
        db.query(ProcessingRecord)
        .filter(ProcessingRecord.recycler_id == recycler.id)
        .order_by(ProcessingRecord.created_at.desc())
    )
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total, "page": page, "page_size": page_size,
        "items": [ProcessingRecordOut.model_validate(i) for i in items],
    }

# ─── GET /recycler/processing-record/{id} ─────────────────────────────────────
@router.get("/processing-record/{id}", response_model=ProcessingRecordOut, summary="Get a specific processing record")
def get_processing_record(
    id: int,
    db: Session    = Depends(get_db),
    recycler: User = Depends(require_role(UserRole.RECYCLER)),
):
    from fastapi import HTTPException
    record = db.query(ProcessingRecord).filter(ProcessingRecord.id == id, ProcessingRecord.recycler_id == recycler.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Processing record not found")
    return record

# ─── POST /recycler/ai-recommend/{id} ─────────────────────────────────────────
@router.post("/ai-recommend/{id}", summary="Get AI recommendation for a waste batch")
def get_ai_recommendation(
    id: int,
    db: Session    = Depends(get_db),
    recycler: User = Depends(require_role(UserRole.RECYCLER)),
):
    from app.services import recycler_service
    return recycler_service.get_ai_recommendation(db, id)


# ─── POST /recycler/send-payment/{pickup_id} ──────────────────────────────────
from pydantic import BaseModel
class SendPaymentIn(BaseModel):
    amount: float
    note: str | None = None

@router.post("/send-payment/{pickup_id}", status_code=201, summary="Recycler sends monetary payment to the user")
def send_payment(
    pickup_id: int,
    body: SendPaymentIn,
    db: Session    = Depends(get_db),
    recycler: User = Depends(require_role(UserRole.RECYCLER)),
):
    from app.services import recycler_service
    return recycler_service.send_payment(db, recycler, pickup_id, body.amount, body.note)


# ─── GET /recycler/my-payments ────────────────────────────────────────────────
@router.get("/my-payments", summary="List payments sent by this recycler")
def my_payments(
    page: int      = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session    = Depends(get_db),
    recycler: User = Depends(require_role(UserRole.RECYCLER)),
):
    from app.services import recycler_service
    total, items = recycler_service.get_payments_for_recycler(db, recycler.id, page, page_size)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": p.id,
                "pickup_id": p.pickup_id,
                "user_id": p.user_id,
                "amount": p.amount,
                "waste_item": p.waste_item,
                "note": p.note,
                "created_at": p.created_at.isoformat(),
            }
            for p in items
        ],
    }

