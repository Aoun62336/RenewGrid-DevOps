"""
final_test.py — End-to-end auth test against the live server.
Verifies the password hash stored in DB matches Admin@1234, then POSTs to the live API.
"""
import os, sys, urllib.request, json
os.environ.setdefault("PASSLIB_SUPPRESS_BCRYPT_VERSION_WARNING", "1")
sys.path.append('.')

import app.main  # register all models
from app.db.database import SessionLocal
from app.core.security import verify_password
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.email == 'admin@renewgrid.com').first()
db.close()

print("=== DB CHECK ===")
print(f"Hash in DB: {user.password_hash[:40]}...")
ok = verify_password('Admin@1234', user.password_hash)
print(f"verify_password('Admin@1234', hash) = {ok}")

if not ok:
    print("ERROR: Hash in DB is still old/broken. Re-run reset_passwords.py")
    sys.exit(1)

print("\n=== LIVE SERVER TEST ===")
url = 'http://localhost:8000/auth/login'
payload = json.dumps({'email': 'admin@renewgrid.com', 'password': 'Admin@1234'}).encode()
req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read())
        print("LOGIN OK! Token:", data['access_token'][:40], "...")
        print("User:", data['user'])
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"HTTP {e.code}: {body}")
    print("\nThe live server is probably serving stale code.")
    print("Please restart uvicorn: python -m uvicorn app.main:app --reload")
