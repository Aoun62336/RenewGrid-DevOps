"""
db/database.py — SQLAlchemy engine, session factory, and Base class.
Import `get_db` as a FastAPI dependency wherever DB access is needed.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# ── Engine & Session ──────────────────────────────────────────────────────────
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,      # detect stale connections automatically
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Declarative Base ──────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """All ORM models inherit from this Base."""
    pass


# ── Dependency ────────────────────────────────────────────────────────────────
def get_db():
    """
    FastAPI dependency that yields a DB session and ensures
    it is closed after every request (even on errors).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
