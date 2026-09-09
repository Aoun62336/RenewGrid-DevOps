"""
main.py — FastAPI application entry point.
"""
import os
os.environ.setdefault("PASSLIB_SUPPRESS_BCRYPT_VERSION_WARNING", "1")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.config import settings

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

limiter = Limiter(key_func=get_remote_address)

# ── Import all models so SQLAlchemy discovers tables ─────────────────────────
from app.models.user import User                                        # noqa
from app.models.waste import WasteUpload, WasteImage                   # noqa
from app.models.core import (                                           # noqa
    PickupRequest, PickupStatusHistory, CollectorProof,
    ProcessingRecord, RecyclerInventory, Reward, AppConfig, PickupReview
)

# ── Routers ───────────────────────────────────────────────────────────────────
from app.routers import auth, users, waste, pickup, collector, recycler, admin, system, notifications

# NOTE: Schema is managed by Alembic. Run `alembic upgrade head` to apply migrations.

# ── App Instance ──────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "**RenewGrid – Integrated E-Waste Lifecycle Management**\n\n"
        "Full backend API with JWT auth, RBAC, and complete e-waste lifecycle.\n\n"
        "**Quick Start:**\n"
        "1. `POST /auth/register` — create account\n"
        "2. `POST /auth/login` — get access_token\n"
        "3. Click **Authorize**, paste token → all protected routes work"
    ),
    version="2.1.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static file serving for uploads ──────────────────────────────────────────
Path("uploads").mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ── Route Registration ────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router,     prefix="/users",     tags=["Users"])
app.include_router(waste.router,     prefix="/waste",     tags=["Waste Uploads"])
app.include_router(pickup.router,    prefix="/pickup",    tags=["Pickup Requests"])
app.include_router(collector.router, prefix="/collector", tags=["Collector"])
app.include_router(recycler.router,  prefix="/recycler",  tags=["Recycler"])
app.include_router(admin.router,     prefix="/admin",     tags=["Admin"])
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
app.include_router(system.router,    prefix="",           tags=["System / Config"])

# ── Exception Handlers ────────────────────────────────────────────────────────
from app.core.exceptions import add_exception_handlers
add_exception_handlers(app)


@app.get("/", tags=["Health"])
def root():
    return {"status": "online", "project": settings.PROJECT_NAME, "docs": "/docs"}
