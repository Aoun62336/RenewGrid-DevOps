# RenewGrid — Frontend SPA

The React 19 frontend provides four fully isolated role dashboards for Admin, User (E-Waste Producer), Collector, and Pickup Recycler. Each dashboard has its own protected route group enforced by a `ProtectedRoute` component that validates the JWT and checks the user's role before rendering.

→ [Full project overview, tech stack, and backend API reference](../README.md)

---

## Technology Stack

| Component | Technology |
| :----- | :----- |
| **Framework** | React 19 |
| **Build tool** | Vite 8 |
| **Routing** | React Router v7 |
| **Styling** | TailwindCSS v3 + custom CSS tokens |
| **Maps** | Leaflet + React-Leaflet |
| **QR scanning** | html5-qrcode |
| **PDF export** | jsPDF + jsPDF-AutoTable |
| **Image cropping** | react-image-crop |
| **Notifications** | react-hot-toast |
| **API client** | Axios (via `src/services/api.js`) |

---

## Route Map

### Public

| Path | Page |
| :----- | :----- |
| `/` | Landing page |
| `/register` | User registration |
| `/login` | Login |
| `/forgot-password` | Forgot password request |
| `/reset-password` | Password reset (token link) |

### User Dashboard (role: `user`)

| Path | Page |
| :----- | :----- |
| `/user-dashboard` | Overview — stats, recent activity |
| `/user/upload-ewaste` | Submit new e-waste item with images |
| `/user/ai-price/:id` | AI price estimation result for a waste upload |
| `/user/schedule-pickup` | Schedule a pickup for a waste item |
| `/pickup/track` | Track all pickups |
| `/pickup/:id/track` | Live status timeline for a specific pickup |
| `/pickup/:id/qr` | QR code display for collector scan verification |
| `/user/recycling-history` | Full recycling history |
| `/user/reward-wallet` | Reward points and CO₂ credits ledger |
| `/user/review-rating` | Submit star rating and comment after pickup |
| `/user/profile` | View and edit profile |
| `/user/change-password` | Change account password |

### Collector Dashboard (role: `collector`)

| Path | Page |
| :----- | :----- |
| `/collector-dashboard` | Overview — today's pickups, stats |
| `/collector/assigned-pickups` | All assigned pickup requests |
| `/collector/route-optimization` | Map view of assigned pickup locations |
| `/collector/scan-qr` | QR code scanner for pickup verification |
| `/collector/upload-proof` | Upload photographic proof of collection |
| `/collector/update-status` | Manually advance pickup status |
| `/collector/availability` | Toggle on/off availability for new assignments |
| `/collector/reviews` | View user reviews and ratings received |
| `/collector/change-password` | Change account password |

### Recycler Dashboard (role: `recycler`)

| Path | Page |
| :----- | :----- |
| `/dashboard` | Overview — delivered batches, processing stats |
| `/collected-waste-listing` | All waste batches assigned to this recycler |
| `/waste-receipt/:id` | Waste batch detail and receipt view |
| `/ai-recommendation/:id` | AI processing recommendation for a batch |
| `/processing-decision/:id` | Submit recycle or refurbish decision |
| `/inventory-management` | Current material stock and status |
| `/processing-history` | History of all completed processing records |
| `/recycler/profile` | View and edit profile |
| `/recycler/change-password` | Change account password |

### Admin Dashboard (role: `admin`)

| Path | Page |
| :----- | :----- |
| `/admin-dashboard` | Platform-wide KPI overview |
| `/admin/user-management` | View, block, unblock all users |
| `/admin/add-user` | Create a new user account |
| `/admin/collector-management` | Manage collector accounts |
| `/admin/add-collector` | Create a new collector account |
| `/admin/waste-assignment` | Assign pending pickups to collectors and recyclers |
| `/admin/recycler-approval` | Approve recycler facility registrations |
| `/admin/waste-analytics` | Waste volume and category breakdown |
| `/admin/revenue-tracking` | Revenue aggregation across recyclers |
| `/admin/co2-analytics` | CO₂ savings tracking and totals |
| `/admin/pickup-statistics` | Pickup counts by status and date range |
| `/admin/area-analytics` | Geographic distribution of pickups |
| `/admin/trend-forecasting` | Volume and revenue trend charts |
| `/admin/pricing-rules` | Create and update AI pricing rules per category |
| `/admin/waste-uploads` | View all submitted waste uploads |
| `/admin/assign-reward-points` | Manually assign reward points to users |
| `/admin/reports` | Generate and export PDF platform reports |
| `/admin/profile` | Admin profile management |
| `/admin/change-password` | Change admin account password |

---

## Environment Variables

Create a `.env` file in the `frontend/` directory (`.env.*` is gitignored; do not commit it):

```env
VITE_API_BASE_URL=http://localhost:8000
```

The `.env.production` file follows the same pattern for production deployments.

---

## Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`. The Vite dev server proxies API calls to the backend at the URL defined in `VITE_API_BASE_URL`.

| Command | Purpose |
| :----- | :----- |
| `npm run dev` | Start Vite development server with HMR |
| `npm run build` | Build production bundle to `dist/` |
| `npm run preview` | Preview the production build locally |
| `npm run lint` | Run ESLint across the source tree |
