# RenewGrid — Backend API Server

The FastAPI backend is the business engine for the RenewGrid platform. It manages identity and authentication, enforces role-based access control across four user types, runs the AI price estimation logic, processes the pickup lifecycle state machine, generates and validates QR codes, dispatches transactional emails, and computes reward points and CO₂ savings as background tasks.

→ [Full project overview, tech stack, and setup](../README.md)

---

## API Endpoints

| Router | Prefix | Description |
| :----- | :----- | :----- |
| **Auth** | `/auth` | Register, login, refresh token, logout, update profile, upload profile image, forgot/reset/change password, delete account |
| **Users** | `/users` | Authenticated user profile reads |
| **Waste** | `/waste` | Upload e-waste items with images; AI estimation on create; paginated user upload history |
| **Pickup** | `/pickup` | Schedule pickup, track status, retrieve QR code, submit review and rating |
| **Collector** | `/collector` | Accept/reject assignments, upload collection proof, update status, set availability, view reviews |
| **Recycler** | `/recycler` | Receive delivered waste, start and update processing, manage inventory, log payments |
| **Admin** | `/admin` | Full user management, pickup assignment, analytics, pricing rules, reward point assignment, PDF reports |
| **Notifications** | `/notifications` | Fetch and mark-read in-app notification feed |
| **System** | `/` | Health check, app config reads |

Interactive documentation (Swagger UI) is available at `http://localhost:8000/docs` when the server is running.

---

## Architecture

The backend follows a layered architecture with strict separation of concerns:

```
HTTP Request
    │
    ▼
Router (routers/)           ← Validates input via Pydantic schemas; enforces auth dependency
    │
    ▼
Service (services/)         ← All business logic, state machine transitions, background tasks
    │
    ▼
Repository (repositories/)  ← All database queries; no business logic
    │
    ▼
SQLAlchemy ORM (models/)    ← Declarative table definitions; typed Mapped columns
    │
    ▼
PostgreSQL
```

The repository pattern ensures that service logic is never coupled to raw queries. Services call repositories; repositories call the ORM; routers call services. This makes each layer independently testable and replaceable.

---

## Database Schema

| Table | Purpose |
| :----- | :----- |
| `users` | All accounts across Admin, User, Collector, and Recycler roles |
| `waste_uploads` | E-waste submissions with AI inference fields (detected type, confidence, estimated price, CO₂) |
| `waste_images` | One-to-many images per waste upload; one flagged as primary |
| `pickup_requests` | Core lifecycle entity linking user, waste, collector, and recycler with status and geolocation |
| `pickup_status_history` | Immutable audit trail — every status transition with actor, timestamp, and note |
| `collector_proofs` | Photo proof uploaded by collector on collection; one-to-one with pickup |
| `processing_records` | Recycler processing decision (recycle / refurbish) and outcome per pickup |
| `recycler_inventory` | Material stock entries created from processed pickups |
| `recycler_payments` | Monetary payments from recycler to producer per pickup |
| `rewards` | Points and CO₂ credits awarded to producers on pickup completion |
| `notifications` | In-app notification feed; read/unread state per user |
| `app_config` | Key-value store for frontend-consumable configuration |
| `pricing_rules` | Admin-defined pricing per waste category; used by AI estimator |
| `pickup_reviews` | Star rating and comment left by producer after pickup completion |

---

## Setup

### Environment Configuration

```bash
cd backend
copy .env.example .env
```

Edit `.env` with your values:

```env
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@localhost:5432/renewgrid"
SECRET_KEY="generate with: openssl rand -hex 32"
REFRESH_SECRET_KEY="generate with: openssl rand -hex 32"
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-gmail-app-password
```

### Virtual Environment and Dependencies

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### Seed the Database

```bash
python scripts/seed.py
```

Creates all tables (bypassing Alembic for local development) and inserts default configuration values and demo user accounts.

### Run

```bash
uvicorn app.main:app --reload
```

### Utility Scripts

| Script | Purpose |
| :----- | :----- |
| `scripts/seed.py` | Creates all tables and inserts demo users and config |
| `scripts/reset_passwords.py` | Force-resets all demo account passwords to defaults |
| `scripts/fix_db_schema.py` | One-off schema patches for manual migration edge cases |
