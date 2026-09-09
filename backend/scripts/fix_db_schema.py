
import psycopg2
from app.core.config import settings

def fix_db():
    print(f"Connecting to database...")
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        cur = conn.cursor()
        print("Adding recycler_id column to pickup_requests table...")
        cur.execute("ALTER TABLE pickup_requests ADD COLUMN IF NOT EXISTS recycler_id INTEGER REFERENCES users(id);")
        conn.commit()
        print("Success: Column recycler_id added or already exists.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Failed to update database: {e}")

if __name__ == "__main__":
    fix_db()
