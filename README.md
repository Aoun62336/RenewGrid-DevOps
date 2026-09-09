# RenewGrid: AI-Powered E-Waste Recycling & Rewards Platform

<!-- Application Stack -->
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

<!-- Frontend Tooling -->
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-38BDF8?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Leaflet](https://img.shields.io/badge/Leaflet-199900?style=for-the-badge&logo=leaflet&logoColor=white)](https://leafletjs.com/)

<!-- Data & Auth -->
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=python&logoColor=white)](https://www.sqlalchemy.org/)
[![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)

---

RenewGrid is a full-stack e-waste lifecycle management platform that connects consumers, pickup collectors, and recycling facilities under a single system. Users submit e-waste, collectors coordinate pickups with QR-based verification, and recyclers process and close the loop — with AI-estimated pricing and a reward points system tracking environmental impact at every step.

**Admin** creates and manages all users across roles, assigns pickups to collectors and recyclers, monitors platform-wide analytics, configures AI pricing rules per waste category, and has unrestricted access to all data, reports, and reward point assignments.

**User (E-Waste Producer)** uploads e-waste items with photos and metadata, receives an AI-estimated valuation and credit point estimate, schedules a pickup at a chosen address and date, tracks pickup status in real time via a live timeline, displays a QR code for collector identity verification, and views recycling history and earned reward wallet.

**Collector** views assigned pickups on an interactive map, accepts or rejects assignments, updates status through each stage of the pickup lifecycle, uploads photographic proof of collection, and records the final collected weight and price upon delivery.

**Recycler** receives delivered waste batches from collectors, starts processing with a decision (recycle or refurbish), updates inventory, logs direct payments to users, and marks pickups as completed — automatically triggering reward point and CO₂ credit generation for the producer.

→ [Full API reference, repository pattern, and database schema](backend/README.md)

**Application layer:** React 19 + FastAPI + PostgreSQL

---

## What I Implemented

| Area | What I implemented | Repository evidence |
| :----- | :----- | :----- |
| **AI pricing engine** | Rule-based estimator that reads admin-defined `PricingRule` rows from the database; applies category base price, per-kg rate, and condition multipliers (working / partial / broken); falls back to hardcoded category rates if no active rule exists for the given category | `backend/app/services/waste_service.py` |
| **JWT authentication** | Dual-token system with configurable short-lived access tokens and 7-day refresh tokens; all protected routes verified via `get_current_user` FastAPI dependency; login endpoint rate-limited at 5 requests/minute via slowapi | `backend/app/core/security.py`, `backend/app/routers/auth.py` |
| **RBAC — 4 role system** | Role enum enforced at the API layer through FastAPI dependency injection and at the frontend through `ProtectedRoute` wrappers; Admin, User, Collector, and Recycler each access a completely isolated dashboard with no route overlap | `backend/app/core/deps.py`, `frontend/src/components/auth_routes/` |
| **Pickup lifecycle state machine** | 12-state status enum (`PENDING → ASSIGNED → IN_PROGRESS → PROOF_UPLOADED → COLLECTED → DELIVERED → PROCESSING → COMPLETED`); every transition is validated against the current state and persisted to an immutable `pickup_status_history` audit table with actor ID and timestamp | `backend/app/models/core.py`, `backend/app/services/collector_service.py`, `backend/app/services/recycler_service.py` |
| **QR code verification** | Server-generated QR codes per pickup request, rendered in the user's dashboard; scanned by the collector's device camera using html5-qrcode; verifies pickup identity before allowing status progression | `backend/app/routers/pickup.py`, `frontend/src/pages/user/QRDisplay.jsx`, `frontend/src/pages/collector/CollectorPages.jsx` |
| **Reward & CO₂ engine** | Background task triggered on pickup completion; awards points at 10 pts/kg and calculates CO₂ saved at 0.5 kg/kg of waste collected; idempotent — checks for existing reward before inserting; pushes an in-app notification to the user on success | `backend/app/services/reward_service.py` |
| **Collector proof upload** | Collectors upload a photo as evidence of collection; file validated by content type and size (5 MB cap); stored to `uploads/proofs/` and linked to the pickup record via a dedicated `CollectorProof` model | `backend/app/services/collector_service.py`, `backend/app/models/core.py` |
| **Transactional email** | Password-reset flow with an HTML email template dispatched via SMTP as a FastAPI `BackgroundTask`; STARTTLS Gmail-compatible; 30-minute token expiry; credentials and frontend URL read from environment variables | `backend/app/services/email_service.py` |
| **Repository pattern** | Decoupled data access layer separating all query logic from service and router logic; one repository module per domain (user, waste, pickup, collector, recycler) | `backend/app/repositories/` |
| **Admin analytics** | Dashboard aggregates across users, waste, pickups, revenue, CO₂ saved, and geographic area; trend forecasting, pricing rule management, user/collector creation, reward point assignment, and PDF report export | `backend/app/services/admin_service.py`, `frontend/src/pages/admin/AdminPages.jsx` |
| **File upload handling** | Profile images and waste photos validated on content type (JPEG / PNG / WebP / GIF) and file size (5 MB cap); saved with UUID-prefixed filenames to role-specific subdirectories under `uploads/` and served as FastAPI static files | `backend/app/routers/auth.py`, `backend/app/services/waste_service.py` |

---

## Technology Stack

### Application Layer

| Component | Technology |
| :----- | :----- |
| **Frontend** | React 19 · Vite 8 · React Router v7 |
| **Backend** | Python · FastAPI · SQLAlchemy · Alembic |
| **Database** | PostgreSQL |
| **Authentication** | JWT via python-jose and passlib/bcrypt |
| **Maps** | Leaflet + React-Leaflet |
| **PDF generation** | jsPDF + jsPDF-AutoTable |
| **QR scanning** | html5-qrcode |
| **Styling** | TailwindCSS v3 |
| **Rate limiting** | slowapi |
| **Email** | Python smtplib (STARTTLS / Gmail App Password) |

### Full Stack Overview

| Technology | How it is used | Why it was used |
| :----- | :----- | :----- |
| **FastAPI** | REST API server; all business logic, authentication, file serving, and background tasks | Auto-generates OpenAPI/Swagger docs, native Pydantic v2 validation, async-capable, production-grade |
| **SQLAlchemy** | ORM for all database models, queries, and relationships | Declarative `Mapped` typed columns, relationship management, decoupled from raw SQL |
| **Alembic** | Database migration management | Version-controlled schema evolution alongside source code |
| **PostgreSQL** | Primary relational database | ACID compliance, native enum type support, production-grade reliability |
| **React 19** | Single-page application with four fully isolated role dashboards | Component model, concurrent rendering, broad ecosystem |
| **Vite 8** | Frontend build tool and dev server | Sub-second HMR, ESM-native, minimal configuration overhead |
| **TailwindCSS v3** | Utility-first styling across all dashboards | Rapid, consistent UI development without context-switching from JSX |
| **Leaflet** | Interactive map for collector route and location view | Lightweight, open-source, no API key requirement |
| **slowapi** | Request rate limiting middleware on FastAPI | Protects login and password-reset endpoints from brute-force and abuse |
| **python-jose** | JWT encoding, decoding, and verification | Lightweight, supports HS256, handles access and refresh token rotation cleanly |
| **qrcode** | Server-side QR code image generation | Generates pickup verification codes without external service dependency |

---

## Pickup Status Lifecycle

```
PENDING
  └─► ASSIGNED ──────────────────────────────────────────► REJECTED
        └─► IN_PROGRESS ────────────────────────────────► REJECTED
              └─► PROOF_UPLOADED
                    └─► COLLECTED
                          └─► DELIVERED
                                └─► PROCESSING
                                      └─► COMPLETED ◄─── RECYCLED
                                                └─► CANCELLED (admin)
```

Every transition is recorded in `pickup_status_history` with the actor user ID, timestamp, and an optional note — providing a full, immutable audit trail per pickup.

---

## Setup

### 1. Database

Ensure PostgreSQL is running and create the application database:

```sql
CREATE DATABASE renewgrid;
```

### 2. Backend

```bash
cd backend

# Copy environment template and configure credentials
copy .env.example .env
# Edit .env: set DATABASE_URL, SECRET_KEY, REFRESH_SECRET_KEY
# Optionally set SMTP_HOST, SMTP_USER, SMTP_PASS for email

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate           # Windows PowerShell / CMD
# source venv/bin/activate      # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Create tables and seed demo data
python scripts/seed.py

# Start the API server
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000` · Interactive API docs at `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

### One-command launch (Windows)

```bash
run.bat
```

Opens both the backend and frontend servers in separate terminal windows.

---

## Demo Credentials

| Role | Email | Password |
| :----- | :----- | :----- |
| **Administrator** | `admin@renewgrid.com` | `Admin@1234` |
| **E-Waste Producer** | `user@renewgrid.com` | `User@1234` |
| **Pickup Collector** | `collector@renewgrid.com` | `Collector@1234` |
| **Facility Recycler** | `recycler@renewgrid.com` | `Recycler@1234` |

---

## Project Structure

```text
RenewGrid/
├── backend/                        # FastAPI application server
│   ├── app/
│   │   ├── core/                   # Config, JWT security, dependencies, exception handlers
│   │   ├── db/                     # SQLAlchemy engine and session factory
│   │   ├── models/                 # ORM models: User, WasteUpload, PickupRequest, Reward, ...
│   │   ├── repositories/           # Data access layer — one repository per domain
│   │   ├── routers/                # REST controllers: auth, waste, pickup, collector, recycler, admin
│   │   ├── schemas/                # Pydantic request and response schemas
│   │   └── services/               # Business logic: AI estimator, rewards, email, admin analytics
│   ├── migrations/                 # Alembic migration scripts
│   ├── scripts/                    # seed.py · reset_passwords.py · fix_db_schema.py
│   ├── uploads/                    # Runtime file storage (gitignored — .gitkeep preserves directory)
│   ├── .env.example                # Environment variable template
│   └── requirements.txt            # Python dependencies
│
└── frontend/                       # React 19 + Vite SPA
    ├── src/
    │   ├── components/             # Shared UI components, layout, and route guards
    │   ├── pages/
    │   │   ├── admin/              # Admin dashboard, user/collector management, analytics, reports
    │   │   ├── collector/          # Assigned pickups, QR scan, proof upload, availability
    │   │   ├── recycler/           # Waste receipt, AI recommendation, processing, inventory
    │   │   └── user/               # Upload, AI price estimate, schedule, tracking, rewards
    │   └── services/               # Axios API service layer (api.js)
    ├── public/                     # Static assets and favicon
    └── index.html                  # Application entry point
```
