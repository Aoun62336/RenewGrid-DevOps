"""
seed.py — Seeds the database with default roles and demo users.
Run ONCE after starting PostgreSQL: python seed.py
"""
import os
import sys

# Fix passlib + bcrypt 4.x compatibility on Python 3.13
os.environ.setdefault("PASSLIB_SUPPRESS_BCRYPT_VERSION_WARNING", "1")

from app.db.database import Base, engine, SessionLocal  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402
from app.models.waste import WasteUpload   # noqa — needed for table creation
from app.models.core import PickupRequest, Reward, ProcessingRecord  # noqa
from app.core.security import hash_password

# Create all tables
Base.metadata.create_all(bind=engine)


DEMO_USERS = [
    {
        "full_name": "Super Admin",
        "email": "admin@renewgrid.com",
        "phone_number": "9000000001",
        "password": "Admin@1234",
        "role": UserRole.ADMIN,
    },
    {
        "full_name": "John Doe",
        "email": "user@renewgrid.com",
        "phone_number": "9000000002",
        "password": "User@1234",
        "role": UserRole.USER,
    },
    {
        "full_name": "Mike Collector",
        "email": "collector@renewgrid.com",
        "phone_number": "9000000003",
        "password": "Collector@1234",
        "role": UserRole.COLLECTOR,
    },
    {
        "full_name": "Green Recycling Co.",
        "email": "recycler@renewgrid.com",
        "phone_number": "9000000004",
        "password": "Recycler@1234",
        "role": UserRole.RECYCLER,
    },
]


def seed() -> None:
    db = SessionLocal()
    try:
        created = 0
        for data in DEMO_USERS:
            exists = db.query(User).filter(User.email == data["email"]).first()
            if exists:
                print(f"  [skip] {data['email']} already exists.")
                continue
            user = User(
                full_name=data["full_name"],
                email=data["email"],
                phone_number=data["phone_number"],
                password_hash=hash_password(data["password"]),
                role=data["role"],
            )
            db.add(user)
            created += 1
        db.commit()
        print(f"\nSeeding complete -- {created} new user(s) created.\n")
        if created:
            print("Demo credentials:")
            for u in DEMO_USERS:
                print(f"  {u['role'].value:10} | {u['email']:35} | {u['password']}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
