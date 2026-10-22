"""
migrations/env.py — Alembic environment configuration for RenewGrid.

Key decisions:
  • Database URL is pulled from app.core.config.settings (reads .env) so there
    is a single source of truth — no need to duplicate it in alembic.ini.
  • All ORM models are imported here so Alembic's autogenerate can detect
    every table and produce accurate diffs.
  • compare_type=True ensures column TYPE changes are detected, not just
    structural additions/removals.
"""
import os
# Suppress passlib's bcrypt version warning before any app imports
os.environ.setdefault("PASSLIB_SUPPRESS_BCRYPT_VERSION_WARNING", "1")

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ── Alembic config object ─────────────────────────────────────────────────────
config = context.config

# Set up Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Pull DATABASE_URL from app settings (reads .env) ─────────────────────────
from app.core.config import settings          # noqa: E402
# NOTE: Do NOT use config.set_main_option here — configparser chokes on
# percent-encoded characters in URLs (e.g. %40 for @). Instead we pass
# the URL / engine directly to Alembic's context below.

# ── Import Base + ALL models so autogenerate can see every table ──────────────
from app.db.database import Base             # noqa: E402, F401

from app.models.user import User, AuthSession             # noqa: E402, F401
from app.models.waste import WasteUpload, WasteImage  # noqa: E402, F401
from app.models.core import (                # noqa: E402, F401
    PickupRequest,
    PickupStatusHistory,
    CollectorProof,
    ProcessingRecord,
    RecyclerInventory,
    Reward,
    AppConfig,
    PickupReview,
    Notification,
)

target_metadata = Base.metadata


# ── Offline mode (no live DB connection) ──────────────────────────────────────
def run_migrations_offline() -> None:
    """
    Emit migration SQL to stdout without connecting to the database.
    Useful for reviewing SQL before applying, or for environments without
    direct DB access.
    """
    # Escape % signs so configparser interpolation doesn't break on
    # percent-encoded chars in the URL (e.g. %40 for @).
    url = settings.DATABASE_URL.replace("%", "%%")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online mode (live DB connection) ──────────────────────────────────────────
def run_migrations_online() -> None:
    """
    Connect to the database and apply migrations within a transaction.
    This is the normal mode used by `alembic upgrade head`.
    """
    # Re-use the app's own engine so we never duplicate connection config.
    from app.db.database import engine as _engine  # noqa: E402

    with _engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
