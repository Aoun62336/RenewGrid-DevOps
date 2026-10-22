"""
Explicit, development-only RenewGrid demo account seeding.

Run database migrations separately before this script.
Never run this script as part of production startup.
"""
import os
import sys

os.environ.setdefault("PASSLIB_SUPPRESS_BCRYPT_VERSION_WARNING", "1")

from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.user import User, UserRole

# Register related ORM mappings so relationships resolve without errors.
import app.models.waste  # noqa: F401
import app.models.core   # noqa: F401

DEMO_ACCOUNTS = (
    ("ADMIN",     UserRole.ADMIN,     "Development Admin"),
    ("USER",      UserRole.USER,      "Development User"),
    ("COLLECTOR", UserRole.COLLECTOR, "Development Collector"),
    ("RECYCLER",  UserRole.RECYCLER,  "Development Recycler"),
)


def require_development_environment() -> None:
    environment = os.getenv("APP_ENV", "").strip().lower()
    enabled = os.getenv("ENABLE_DEMO_SEED", "").strip().lower()

    if environment not in {"development", "test"}:
        raise RuntimeError(
            "Demo seeding is permitted only in development or test.\n"
            f"  APP_ENV={environment!r}"
        )
    if enabled != "true":
        raise RuntimeError(
            "Set ENABLE_DEMO_SEED=true to explicitly enable demo seeding."
        )


def load_accounts() -> list[dict]:
    accounts = []
    passwords = []

    for key, role, name in DEMO_ACCOUNTS:
        email_var = f"DEMO_{key}_EMAIL"
        pass_var = f"DEMO_{key}_PASSWORD"

        email = os.getenv(email_var, "").strip()
        password = os.getenv(pass_var, "").strip()

        if not email:
            print(f"  [skip] {email_var} is not set — skipping {name}.")
            continue
        if not password:
            print(f"  [skip] {pass_var} is not set — skipping {name}.")
            continue

        accounts.append(
            {
                "full_name": name,
                "email": email,
                "password": password,
                "role": role,
            }
        )
        passwords.append(password)

    # Refuse to seed if any two accounts share the same password.
    if len(passwords) != len(set(passwords)):
        raise RuntimeError(
            "Demo accounts must each use a unique password. "
            "Check your DEMO_*_PASSWORD environment variables."
        )

    return accounts


def seed() -> None:
    require_development_environment()
    accounts = load_accounts()

    if not accounts:
        print("No demo accounts configured.  Nothing to seed.")
        return

    db = SessionLocal()
    try:
        created = 0
        for data in accounts:
            exists = db.query(User).filter(User.email == data["email"]).first()
            if exists:
                print(f"  [skip] {data['email']} already exists.")
                continue
            user = User(
                full_name=data["full_name"],
                email=data["email"],
                password_hash=hash_password(data["password"]),
                role=data["role"],
            )
            db.add(user)
            created += 1
        db.commit()
        print(f"\nSeeding complete — {created} new account(s) created.")
    except IntegrityError as exc:
        db.rollback()
        print(f"IntegrityError during seeding: {exc}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
