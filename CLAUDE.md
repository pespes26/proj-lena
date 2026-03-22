# סנג'ר של לנה — FM Financial Dashboard

## Project Overview
מערכת ניהול P&L ותזרים מזומנים לחברת FM. הכל בעברית, כיוון RTL.
מנהלת פרויקטי תחזוקה ו-FM עם מעקב הכנסות, הוצאות, רווח תפעולי ותזרים מזומנים.

## Tech Stack
- **Frontend:** Vue 3 (Composition API, `<script setup>`) + Vite 5 + Tailwind CSS 3
- **Backend:** Python + FastAPI + uvicorn
- **Charts:** Chart.js 4 + vue-chartjs 5
- **HTTP:** Axios
- **Data:** Excel (openpyxl/pandas) → JSON persistence
- **No router** — tab-based SPA via `activeTab` ref in App.vue

## Architecture

### Directory Structure
```
Lena/
├── backend/
│   ├── main.py          # FastAPI app — all endpoints
│   ├── data_loader.py   # Excel parsing logic
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue              # Main layout (sidebar + content)
│   │   ├── main.js              # Entry point
│   │   ├── style.css            # Global styles + iOS design tokens
│   │   ├── services/api.js      # All API calls + formatters
│   │   └── components/          # 20 Vue components
│   ├── vite.config.js           # Proxy /api → localhost:8000
│   ├── tailwind.config.js       # iOS-inspired theme
│   └── package.json
├── data.xlsx                    # Source data (2 sheets)
├── projects_data.json           # Form-created project data
├── reports.json                 # Spot reports
├── attendance_data.json         # Parsed attendance
└── .claude/launch.json          # Dev server config
```

### Data Sources (Excel Sheets)
- **"פרוייקטים מנרב IFM"** — P&L per project per month (revenue, expenses, profit)
- **"ריכוז"** — Cumulative cash flow

### API Pattern
- All endpoints under `/api/`
- Responses: `{ data: ... }`, `{ projects: [...] }`, `{ reports: [...] }`
- Hebrew error messages via `HTTPException`
- Query params for filtering: `?project=שם_פרויקט`

### State Management
- No Vuex/Pinia — component-level `ref()` + `computed()`
- `api.js` service module for all HTTP calls
- Tab navigation: `activeTab` controls which view renders
- Project selection: `selectedProject` ref

## Design System
- **iOS-inspired** glassmorphic UI
- **Primary color:** Teal (#0D9488)
- **Cards:** `.ios-card` class — white, rounded-2xl, shadow-sm, border-gray-100
- **RTL:** `dir="rtl"` on root, all text right-aligned
- **Language:** Hebrew throughout (labels, errors, tooltips)

## Key Components

### Pages (rendered by activeTab)
| Tab | Component | Description |
|-----|-----------|-------------|
| `home` | `Dashboard.vue` | KPIs, revenue/expense charts, project cards |
| `pnl-{project}` | `PnlView.vue` | Per-project P&L with drill-down, reports, form |
| `cashflow` | `CashFlowView.vue` | Cumulative cash flow, monthly net |
| `alerts` | `AlertsView.vue` | Risk alerts (margin < threshold) |
| `data` | `DataView.vue` | Excel upload, backups |
| `attendance` | `AttendanceView.vue` | Attendance upload, split by project |

### Charts (all use vue-chartjs)
- `PnlChart` — Line: monthly revenue vs expenses
- `CashFlowChart` — Area: cumulative flow
- `ProfitBarChart` — Bar: profit margins
- `ProjectCompareChart` — Multi-project comparison
- `RevenueExpenseChart` — Dual-axis revenue/expenses
- `MonthlyNetChart` / `ProjectNetChart` — Net monthly flow
- `ExpenseBreakdown` — Doughnut: expense categories

### Modals
- `ProjectFormModal` — Multi-step wizard (details → revenue → expenses)
- `ReportModal` — Spot report (expense/revenue/note/issue)
- `DatePicker` — Custom date selector

## Running the App

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npx vite --port 3000
```

Or use `.claude/launch.json` with `preview_start("frontend")`.

Vite proxies `/api` → `http://localhost:8000`.

## Conventions

### Code Style
- Vue: `<script setup>` composition API, no Options API
- Single-file components: `<template>` → `<script setup>` → `<style>` (rare, mostly Tailwind)
- API functions exported individually from `api.js`
- Hebrew variable names avoided — use English with Hebrew in UI strings only

### File Naming
- Components: PascalCase (`PnlView.vue`, `CashFlowChart.vue`)
- Services: camelCase (`api.js`)
- Backend: snake_case (`data_loader.py`)

### Adding a New Page
1. Create component in `frontend/src/components/`
2. Import in `App.vue`
3. Add sidebar button with tab key
4. Add `v-else-if="activeTab === 'key'"` in content area

### Adding a New API Endpoint
1. Add route in `backend/main.py`
2. Add export function in `frontend/src/services/api.js`
3. Call from component with error handling

### Adding a New Chart
1. Create component using vue-chartjs (`Bar`, `Line`, `Doughnut`, etc.)
2. Register required ChartJS components
3. Use teal color palette: `#0D9488`, `#22c55e`, `#06b6d4`, `#8b5cf6`, `#f59e0b`
4. RTL tooltips: `{ rtl: true, cornerRadius: 12 }`

## JSON Data Files (not in git)
- `data.xlsx` — Source financial data
- `projects_data.json` — Project form entries
- `reports.json` — Spot reports
- `attendance_data.json` — Parsed attendance records

## Important Notes
- All financial values in ₪ (ILS)
- Months: 1-12 (ינואר-דצמבר)
- Revenue forecast: percentage-based (must sum to 100%)
- Expense lines: category + monthly amount + start/end month
- Attendance: auto-splits by project number, calculates cost via hourly rate
