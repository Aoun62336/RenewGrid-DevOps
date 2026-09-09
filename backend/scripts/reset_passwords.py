"""
reset_passwords.py — Resets all demo user passwords using the fixed bcrypt directly.
Run once after fixing security.py: python reset_passwords.py
"""
import os
os.environ.setdefault("PASSLIB_SUPPRESS_BCRYPT_VERSION_WARNING", "1")

import sys
sys.path.append('.')

import app.main  # ensures all models are registered
from app.db.database import SessionLocal
from app.core.security import hash_password, verify_password
from app.models.user import User

RESET_PASSWORDS = [
    ("admin@renewgrid.com",     "Admin@1234"),
    ("user@renewgrid.com",      "User@1234"),
    ("collector@renewgrid.com", "Collector@1234"),
    ("recycler@renewgrid.com",  "Recycler@1234"),
]

db = SessionLocal()
try:
    for email, pw in RESET_PASSWORDS:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.password_hash = hash_password(pw)
            print(f"[OK] Reset password for {email}")
        else:
            print(f"[SKIP] {email} not found")
    db.commit()
    print("\nAll passwords reset. Verifying...")
    for email, pw in RESET_PASSWORDS:
        user = db.query(User).filter(User.email == email).first()
        if user:
            ok = verify_password(pw, user.password_hash)
            print(f"  {'✓' if ok else '✗'} {email}: {pw} → {'PASS' if ok else 'FAIL'}")
finally:
    db.close()
