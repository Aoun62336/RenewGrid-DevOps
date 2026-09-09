"""
routers/waste.py — Waste upload endpoints.
Supports multipart file upload (up to 5 images) + JSON body via Form fields.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.models.waste import WasteCategory
from app.schemas.waste import WasteUploadResponse
from app.services import waste_service

router = APIRouter()

# ─── POST /waste/upload ───────────────────────────────────────────────────────
@router.post("/upload", response_model=WasteUploadResponse, status_code=201,
             summary="Upload e-waste item (multipart)")
def upload_waste(
    background_tasks: BackgroundTasks,
    title: str            = Form(...),
    category: WasteCategory = Form(...),
    estimated_weight: float = Form(...),
    description: Optional[str] = Form(None),
    condition: Optional[str]   = Form(None),
    quantity: int              = Form(1),
    images: List[UploadFile]   = File(default=[]),
    db: Session          = Depends(get_db),
    current_user: User   = Depends(get_current_user),
):
    return waste_service.create_waste_upload(
        db=db,
        user_id=current_user.id,
        title=title,
        category=category,
        estimated_weight=estimated_weight,
        background_tasks=background_tasks,
        description=description,
        condition=condition,
        quantity=quantity,
        images=images
    )

# ─── GET /waste/my-uploads ────────────────────────────────────────────────────
@router.get("/my-uploads", response_model=dict, summary="Paginated list of my uploads")
def my_uploads(
    page: int      = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session    = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total, items = waste_service.get_user_uploads(db, current_user.id, page, page_size)
    return {"total": total, "page": page, "page_size": page_size,
            "items": [WasteUploadResponse.model_validate(i) for i in items]}

# ─── GET /waste/{waste_id} ────────────────────────────────────────────────────
@router.get("/{waste_id}", response_model=WasteUploadResponse, summary="Get waste detail")
def get_waste(
    waste_id: int,
    db: Session    = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return waste_service.get_waste_by_id(db, waste_id, current_user)
