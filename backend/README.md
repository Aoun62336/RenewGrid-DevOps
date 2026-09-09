# RenewGrid — Backend API Server

The FastAPI backend handles authentication, role enforcement, the pickup lifecycle state machine, AI price estimation, QR code generation, file uploads, reward calculation, and transactional email. All configuration is read from a `.env` file through a Pydantic `BaseSettings` class.

→ [Project overview, tech stack, and setup](../README.md)

---

## API Endpoints

| Router | Prefix | Description |
| :----- | :----- | :----- |
| **Auth** | `/auth` | Register, login, refresh token, logout, profile update, profile image upload, forgot password, reset password, change password, delete account |
| **Users** | `/users` | Authenticated user profile reads |
| **Waste** | `/waste` | Upload e-waste items with images; AI estimation runs on create; paginated upload history |
| **Pickup** | `/pickup` | Schedule pickup, track status, retrieve QR code, submit review and rating |
| **Collector** | `/collector` | Accept or reject assignments, upload collection proof, update status, set availability, view reviews received |
| **Recycler** | `/recycler` | Receive delivered waste, submit processing decision, manage inventory, log payments to users |
| **Admin** | `/admin` | Full user management, pickup assignment, analytics, pricing rules, reward point assignment, PDF reports |
| **Notifications** | `/notifications` | Fetch and mark-read in-app notifications |
| **System** | `` | Health check at `/`, app config reads |

Interactive docs are available at `http://localhost:8000/docs` when the server is running.

---

## Architecture

```
HTTP Request
    |
    v
Router  (routers/)
    Validates input via Pydantic schemas
    Enforces authentication via FastAPI dependencies
    |
    v
Service  (services/)
    All business logic
    State machine transitions
    Background task dispatch
    |
    v
Repository  (repositories/)
    All database queries
    No business logic
    |
    v
SQLAlchemy ORM  (models/)
    Declarative table definitions
    Typed Mapped columns
    |
    v
PostgreSQL
```

**Six repository modules:** auth, user, waste, pickup, collector, recycler.

Routers call services. Services call repositories. No query logic appears in routers.

---

## Database Schema

| Table | Purpose |
| :----- | :----- |
| `users` | All accounts across Admin, User, Collector, and Recycler roles |
| `waste_uploads` | E-waste submissions with AI inference fields (detected type, confidence, estimated price, CO2, credit points) |
| `waste_images` | One-to-many images per waste upload; one flagged as primary |
| `pickup_requests` | Core lifecycle entity linking user, waste, collector, and recycler with status and geolocation |
| `pickup_status_history` | Immutable audit trail for every status transition with actor, timestamp, and note |
| `collector_proofs` | Photo proof uploaded by the collector; one-to-one with pickup |
| `processing_records` | Recycler processing decision (recycle or refurbish) and outcome per pickup |
| `recycler_inventory` | Material stock entries created from processed pickups |
| `recycler_payments` | Monetary payments from recycler to producer per pickup |
| `rewards` | Points and CO2 credits awarded to producers on pickup completion |
| `notifications` | In-app notification feed with read/unread state per user |
| `app_config` | Key-value store for frontend-consumable configuration |
| `pricing_rules` | Admin-defined pricing per waste category, used by the AI estimator |
| `pickup_reviews` | Star rating (1 to 5) and comment left by the producer after pickup completion |

---

## Waste Categories

The `WasteCategory` enum defines 7 supported categories:

| Category | Hardcoded base price | Hardcoded per-kg rate |
| :----- | :----- | :----- |
| Laptops and Computers | 8,000 | 500 |
| Mobile Phones | 6,500 | 500 |
| Monitors and Displays | 1,200 | 150 |
| Printers and Peripherals | 800 | 100 |
| Circuit Boards | 1,000 | 1,500 |
| Batteries | 300 | 250 |
| Mixed Electronics | 400 | 150 |

These are the fallback rates. Admin-defined `PricingRule` rows in the database take priority when they exist for a given category.

---

## Setup

### Environment variables

```bash
cd backend
copy .env.example .env
```

Key values in `.env`:

```env
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@localhost:5432/renewgrid"
SECRET_KEY="generate: openssl rand -hex 32"
REFRESH_SECRET_KEY="generate: openssl rand -hex 32"
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-gmail-app-password
```

### Install and run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Create all tables and insert demo users
python scripts/seed.py

uvicorn app.main:app --reload
```

### Utility scripts

| Script | Purpose |
| :----- | :----- |
| `scripts/seed.py` | Creates all tables and inserts four demo user accounts |
| `scripts/reset_passwords.py` | Resets all demo account passwords to their defaults |
| `scripts/fix_db_schema.py` | One-off schema patches for manual migration edge cases |
