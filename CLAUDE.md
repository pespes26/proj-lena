# CLAUDE.md — Logfi (FM Financial Co-Pilot)

> Operating manual for Claude Code in this repo. Read this first, every session.
> Claude replies to the user in **English**. UI strings and user-facing text stay **Hebrew, RTL**.

---

## 0. Current Migration State — READ FIRST

**Phase A is complete. Phase B is next.**

The codebase is mid-migration away from GCP/Firebase. All GCP/Google/Firebase/Anthropic
imports have been removed. The app runs only in `DEV_MODE=true` right now — real auth and
the LLM layer are stubbed out pending Phase B replacements.

### What was removed (Phase A — commit `2c28c49`)
| Removed | Was used for |
|---|---|
| `firebase-admin` | Backend token verification |
| `google-cloud-firestore` | Primary data store |
| `google-cloud-storage` | File/backup storage |
| `google-genai` | Gemini LLM chat |
| `anthropic` | Secondary LLM SDK |
| `firebase ^12.11.0` (npm) | Frontend auth client |
| `frontend/src/firebase.js` | Firebase client init |
| `firebase.json` | Firebase Hosting config |

### What is stubbed (Phase B must replace)
| File | Stub behaviour |
|---|---|
| `backend/auth.py` → `get_current_user` | Non-DEV tokens → HTTP 503 |
| `backend/routers/auth.py` | All user CRUD endpoints → HTTP 503 |
| `backend/services/ai_agents.py` → `chat_stream` | Yields single "Phase B required" message |
| `frontend/src/App.vue` | Auth state = DEV_MODE localStorage check only |
| `frontend/src/components/LoginPage.vue` | Non-DEV login → error string |
| `frontend/src/components/UserProfileModal.vue` | Password change → error string |

### What still works (DEV_MODE=true)
- All financial dashboards, P&L, cash flow
- Project CRUD (reads/writes to local JSON files)
- Risk scoring, what-if (calculator_agent, form_calculator)
- All API endpoints that don't touch auth user management or AI chat

### Phase B task list
- [ ] Choose replacement auth provider (JWT/session-based, or new cloud auth)
- [ ] Choose replacement data store (PostgreSQL recommended; Firestore was the old canonical)
- [ ] Wire in replacement LLM (Claude API via `anthropic` SDK, or other)
- [ ] Implement `get_current_user` with new auth
- [ ] Implement user CRUD in `routers/auth.py`
- [ ] Implement `chat_stream` with new LLM
- [ ] Restore frontend login flow
- [ ] Restore password change in UserProfileModal

---

## 1. Project Overview

**Logfi** (previously "סנג'ר של לנה") is an internal financial dashboard for an Israeli FM (Facility Management) company. Its job is to give Lena and the management team real-time per-project visibility into P&L, cash flow, and risk — replacing a previous world where each project's profitability was invisible until end-of-quarter Excel consolidation.

**Core value (all four matter):**
1. **Per-project P&L visibility** — the original pain point; know which sites make or lose money, each month.
2. **Cash flow forecasting** — cumulative and monthly net liquidity view.
3. **Risk alerts / early warning** — surface projects bleeding margin before they become problems.
4. **AI CFO layer** — the strategic direction. Full AI financial co-pilot: natural-language chat over the data, automated risk scoring, what-if simulations, and forecasting.

**Users:** Lena + a management team of roughly 5–15 people. Mixed technical levels — some want raw numbers, some want "just show me the risk." Role-gated UI today supports at least `admin` and `project_manager` roles (see [App.vue](frontend/src/App.vue)).

**Strategic scope:** Internal tool for **one company only**. Not a SaaS, not multi-tenant. Do **not** introduce multi-tenant primitives (org IDs, tenant isolation, per-tenant config) without explicit approval — it adds complexity the product doesn't need.

**Language & UX:** Everything user-facing is Hebrew, RTL (`dir="rtl"`). All labels, errors, tooltips, chart legends. Code identifiers stay English.

---

## 2. Tech Stack

### Frontend ([frontend/package.json](frontend/package.json))
- **Vue 3.4** — Composition API + `<script setup>` exclusively. No Options API.
- **Vite 5.4** — dev server + build
- **Tailwind CSS 3.4** — styling; iOS-inspired glassmorphic design system
- **Chart.js 4 + vue-chartjs 5** — all charts
- **Axios** — HTTP (token attachment via interceptor in [api.js](frontend/src/services/api.js))
- **html2pdf.js** — PDF export
- **marked** — Markdown rendering (used in AI chat responses)
- **qrcode** — QR generation
- ~~Firebase~~ — **removed in Phase A**; Phase B will add replacement auth

### Backend ([backend/requirements.txt](backend/requirements.txt))
- **FastAPI + uvicorn[standard]** — API layer, also serves built frontend SPA in prod
- **openpyxl + pandas** — Excel parsing for legacy/import flows
- **python-multipart** — file uploads
- ~~firebase-admin~~ ~~google-cloud-firestore~~ ~~google-cloud-storage~~ ~~google-genai~~ ~~anthropic~~ — **all removed in Phase A**

### Runtime
- **Python 3.11** (see [Dockerfile](Dockerfile))
- **Node 20** (Dockerfile frontend build stage)

---

## 3. Repository Structure

```
Lena/
├── backend/
│   ├── main.py                    # FastAPI entrypoint; mounts SPA from frontend/dist in prod
│   ├── auth.py                    # get_current_user dependency — STUBBED (DEV_MODE only)
│   ├── config.py                  # Hardcoded PROJECTS, month maps, expense breakdowns, file paths
│   ├── storage.py                 # JSON-only persistence (Firestore code removed in Phase A)
│   ├── create_user.py             # Admin script for user setup
│   ├── create_test_projects.py    # Seed/demo data script
│   ├── routers/
│   │   ├── auth.py                # /api/auth/* — STUBBED (returns 503 for user CRUD)
│   │   ├── projects.py            # /api/projects/* — CRUD
│   │   ├── project_form.py        # /api/projects/form/* — wizard intake
│   │   ├── dashboard.py           # /api/dashboard/* — aggregated KPIs
│   │   ├── cashflow.py            # /api/cashflow/* — cumulative & monthly net
│   │   ├── reports.py             # /api/reports/* — spot reports
│   │   └── ai.py                  # /api/ai/* — chat stream, whatif, risk-scores
│   ├── services/
│   │   ├── unified.py             # Shared project data access layer
│   │   ├── form_calculator.py     # P&L math from form inputs (SENSITIVE — see §9)
│   │   ├── calculator_agent.py    # Risk scoring, what-if, budget-vs-actual (SENSITIVE)
│   │   ├── ai_agents.py           # LLM system prompt + STUBBED chat_stream
│   │   ├── excel_reader.py        # Legacy Excel import
│   │   └── payment_terms.py       # Payment schedule logic
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue                # Top nav + tab router + role gating
│   │   ├── main.js                # Entry
│   │   ├── style.css              # Global tokens, RTL base
│   │   ├── services/api.js        # All HTTP calls + formatters (single source of truth for API surface)
│   │   └── components/            # ~28 Vue SFCs (pages, charts, modals)
│   ├── vite.config.js             # Proxies /api → localhost:8000 in dev
│   ├── tailwind.config.js
│   └── package.json
├── Dockerfile                     # Multi-stage: build frontend → bundle into Python image → uvicorn
├── CLAUDE.md                      # This file
└── (data.xlsx, *.json, backups/, contracts/)    # Gitignored data artifacts
```

**Note:** `frontend/src/firebase.js` and `firebase.json` were deleted in Phase A.

**Notable currently-disabled features:** `AttendanceView.vue`, `DataView.vue`, `routers/attendance.py`, `routers/data.py` were removed but are **temporarily disabled**, not permanently gone. Do not delete references defensively; do not reintroduce them without asking.

---

## 4. Running the App

### DEV_MODE (only working mode right now)

The app currently requires `DEV_MODE=true` because real auth is stubbed. Add to `backend/.env`:
```
DEV_MODE=true
```
And set `VITE_DEV_MODE=true` in the frontend (`.env.local` or vite env).

The DEV bypass uses a hardcoded token `dev-admin-local` stored in `localStorage`. The backend
`get_current_user` accepts this token and returns a synthetic admin user without any external call.

### Day-to-day local dev: **Docker**
The user runs the app via Docker locally. A production [Dockerfile](Dockerfile) exists (multi-stage: builds Vue frontend, copies into a Python 3.11 image, runs uvicorn serving both API and static SPA).

**Gap Claude may be asked to fix:** there is no `docker-compose.yml` yet for local dev with live reload. If asked to set one up, propose: one service for backend (uvicorn with `--reload`), one for frontend (vite dev server), shared volume for source, proxied via vite. Ask before creating.

### Fallback — bare metal
```bash
# Backend
cd backend && pip install -r requirements.txt
DEV_MODE=true uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (separate terminal)
cd frontend && npm install && VITE_DEV_MODE=true npm run dev
```
Vite dev server runs on port 3000 and proxies `/api/*` → `localhost:8000`.

### Build for production
```bash
docker build -t logfi .
docker run -p 8000:8000 --env-file .env logfi
```
In production the FastAPI app serves the built SPA at `/` and catches all non-`/api` routes via [main.py:33](backend/main.py#L33).

**Note:** Production build is not functional until Phase B auth is implemented.

### Tests
**Stated rule:** a full test suite is required for changes.
**Current reality:** no test suite exists yet in the repo. This is a **gap**, not a settled state. When Claude makes non-trivial changes, it should:
1. Propose adding tests (pytest for backend, Vitest for frontend) alongside the change.
2. For touched financial/AI logic, prioritize writing tests *even if* the surrounding area is untested.
3. When the user explicitly says "skip tests," respect that — but note it in the plan.

Until a test runner is configured, every plan must include a **manual verification checklist** the user can click through.

---

## 5. Architecture & Data Flow

### Data store: **JSON files (current) → Phase B will replace**
After Phase A, all persistence is via local JSON files in [backend/storage.py](backend/storage.py).
Functions are named `*_firestore` for historical reasons but contain no Firestore code.

The JSON files (`projects_data.json`, `reports.json`) are in the gitignored data layer.
The hardcoded `PROJECTS` / `EXPENSE_BREAKDOWN` dicts in [backend/config.py](backend/config.py) are legacy Excel-era constants.

Phase B should introduce a proper data store (PostgreSQL is a natural fit; confirm with user before starting).

### Auth (current state — stubbed)
- **Frontend:** DEV_MODE only — `localStorage.getItem('dev_token')` check in [App.vue](frontend/src/App.vue). No real auth state listener.
- **Backend:** [backend/auth.py](backend/auth.py) — DEV_MODE bypass only. Non-DEV tokens return HTTP 503.
- **Roles:** `admin`, `economist`, `viewer`, `project_manager` defined in `ROLES` dict in auth.py. Role gating in [App.vue](frontend/src/App.vue) is intact; DEV_MODE always returns `admin`.
- **Phase B:** implement `get_current_user` with real token verification and a user store.

### AI layer ([backend/services/ai_agents.py](backend/services/ai_agents.py), [backend/services/calculator_agent.py](backend/services/calculator_agent.py))
- **`chat_stream`** is stubbed — returns a single Hebrew "not available" message. The `SYSTEM_PROMPT` and `_build_projects_context()` are intact and ready for Phase B.
- **Risk scoring / what-if** in `calculator_agent.py` are pure Python math — no LLM dependency, still fully functional.
- **Endpoints** (all under [backend/routers/ai.py](backend/routers/ai.py)):
  - `POST /api/ai/chat` — streaming chat (SSE) — **stubbed**
  - `POST /api/ai/whatif` — scenario simulation — **works**
  - `GET /api/ai/risk-scores` — all projects — **works**
  - `GET /api/ai/risk-score/{project}` — single project — **works**
- **Frontend UI:** [AiChat.vue](frontend/src/components/AiChat.vue), [WhatIfPanel.vue](frontend/src/components/WhatIfPanel.vue), [RiskScoreBadge.vue](frontend/src/components/RiskScoreBadge.vue), [ExecutiveDashboard.vue](frontend/src/components/ExecutiveDashboard.vue).
- **Prompts live in code.** `SYSTEM_PROMPT` is in `ai_agents.py`. See §9 before editing prompts.

### API conventions
- All routes under `/api/`.
- Response shapes: `{ data: ... }`, `{ projects: [...] }`, `{ scores: [...] }` — follow the existing router's shape when adding endpoints.
- Error messages raised via `HTTPException` **in Hebrew**: `raise HTTPException(status_code=404, detail="פרויקט לא נמצא")`.
- All frontend HTTP calls go through [frontend/src/services/api.js](frontend/src/services/api.js). Do not `axios.get` directly from components.

### State management
- No Pinia, no Vuex. Component-local `ref()` + `computed()`.
- `activeTab` ref in [App.vue](frontend/src/App.vue) controls which page renders. No Vue Router today — the user is **open to introducing Vue Router** if there's a clear reason, but it's not required. Don't migrate for its own sake.
- Cross-component state is passed via props or re-fetched from the API. That's the accepted tradeoff; don't invent a global store.

---

## 6. Code Style & Conventions

### Hard rules (violating these is a bug)
- **Hebrew UI, English code.** Every user-visible string in Hebrew. Every identifier, comment, and log line in English.
- **Composition API only.** No `<script>` Options API blocks.
- **Financial values in ₪ (ILS).** Months are 1–12 (the app uses `MONTH_LABELS` starting Sep; see [config.py:82](backend/config.py#L82)).
- **RTL everywhere.** Root has `dir="rtl"`; Chart.js tooltips need `{ rtl: true, cornerRadius: 12 }`.
- **Revenue forecasts must sum to 100%** (percentage-based in the project form).

### Linting & formatting
**Stated rule:** full linting both sides (ESLint + Prettier on frontend, Black + Ruff on backend).
**Current reality:** not yet configured in the repo. If Claude is asked to set it up, do both sides in one PR:
- Frontend: ESLint flat config + Prettier, `lint` and `format` npm scripts.
- Backend: Ruff (lint + format) — modern consolidated choice, faster than Black+Flake8.
- Do **not** silently auto-lint unrelated files when making a change. Wait until the config is in place and the user opts into a sweep.

### Naming
- Components: `PascalCase.vue`
- JS services: `camelCase.js`
- Python modules: `snake_case.py`
- API endpoints: `/api/resource/verb` with kebab-case (e.g. `/api/ai/risk-scores`)

### Design tokens
- Primary: `#0D9488` (teal) / `emerald-800` via Tailwind for brand surfaces
- Cards: `.ios-card` — white, `rounded-2xl`, `shadow-sm`, `border-gray-100`
- Chart palette: `#0D9488`, `#22c55e`, `#06b6d4`, `#8b5cf6`, `#f59e0b`

### Recipes for common work
**New page:**
1. Create SFC in [frontend/src/components/](frontend/src/components/)
2. Import and register as a tab in [App.vue](frontend/src/App.vue)
3. Add role gating (`v-if="isAdmin"` or `v-if="userProfile?.role === '...'"`) if needed
4. Fetch data via [api.js](frontend/src/services/api.js)

**New API endpoint:**
1. Add route in the appropriate `backend/routers/*.py` (create a new router module if it's a new domain, and register it in [backend/main.py](backend/main.py))
2. Add `Depends(get_current_user)` for anything non-public
3. Export a typed function from [api.js](frontend/src/services/api.js)
4. Hebrew error messages via `HTTPException`

**New chart:**
1. vue-chartjs component, registered ChartJS modules imported at top
2. RTL tooltip config, teal palette, consistent card wrapper

---

## 7. How Claude Works in This Repo

The user picked these settings explicitly. Follow them.

### Autonomy: **plan first, then execute**
For any non-trivial change:
1. Read enough of the code to understand the real state (don't guess).
2. Produce a plan: files to touch, exact changes, risks, verification steps.
3. Wait for approval.
4. Execute. Report back with diff summary and verification results.

Trivial fixes (typos, obvious one-line bugs, answering questions) don't need a formal plan.

### When uncertain: **research more, then decide**
Don't ask the user a question you could answer by reading 3 more files. Grep, read, verify, *then* either proceed with confidence or come back with a specific, narrow question. Vague "what do you think?" questions are not welcome — if you ask, give the user 2–3 concrete options with your recommendation.

### Communication style
- Reply in **English**. UI strings in Hebrew.
- **Adaptive verbosity:** terse action-first for small tasks; step-by-step reasoning for complex/risky changes (financial logic, auth, migrations).
- No trailing summary of obvious diffs. The user reads diffs.
- Lead with the answer or action, not the preamble.

### Commits
Descriptive multi-line style:
```
Short imperative title (<72 chars)

Body explaining the *why*: what problem this solves, what the user
was seeing, and any non-obvious tradeoffs. Reference files and
functions if it helps future-reader navigate.
```
Never commit unless the user asks. Never `--amend` without being told.

### Primary task mix (in rough order of frequency)
1. **Phase B implementation** — auth replacement, data store, LLM wiring
2. **New features** — AI-driven, dashboard views, role flows
3. **AI prompt & agent tuning** — improving [ai_agents.py](backend/services/ai_agents.py) prompts, tool definitions, context building
4. **Bug fixes** — across any area

Refactors are welcome but should be explicit and scoped, never snuck in alongside feature work.

---

## 8. Current Hot Zones (in flux — treat with care)

These areas are actively changing and more likely to have rough edges. Read carefully before editing.

1. **Auth stubs** — `backend/auth.py` and `backend/routers/auth.py` are intentionally hollow. Phase B will fill them in. Don't add workarounds that assume the old Firebase shape.
2. **Financial calculations** — [backend/services/form_calculator.py](backend/services/form_calculator.py), [backend/services/calculator_agent.py](backend/services/calculator_agent.py). Small changes to P&L math ripple into every dashboard number and every AI risk score. See §9.
3. **AI features** — `chat_stream` is stubbed; risk scoring and what-if are live. [AiChat.vue](frontend/src/components/AiChat.vue) will show the stub message until Phase B.
4. **Storage layer** — `storage.py` functions are named `*_firestore` but contain only JSON code. Phase B will rename/replace them with the real data store client.

---

## 9. Do Not Touch Without Explicit Approval

These areas are **locked** by default. If a task seems to require touching them, stop and ask.

1. **Auth stubs — shape must stay stable.**
   `backend/auth.py` exports `get_current_user`, `require_admin`, `require_editor`, `check_project_owner`, `db`, `DEV_MODE`. Do not rename or remove these — every router depends on them. Phase B fills in the bodies, not the signatures.

2. **Financial calculation formulas.**
   `form_calculator.py`, the P&L math in `calculator_agent.py`, revenue/expense aggregation, margin calculations. Reason: these numbers drive management decisions and the user has been burned by silent formula changes. Reading is fine; changing requires the user to explicitly say "edit the formula" and review the diff line-by-line.

3. **AI system prompts.**
   The `SYSTEM_PROMPT` and context-builder in [backend/services/ai_agents.py](backend/services/ai_agents.py) shape what the AI CFO says to the user. Prompt tuning is a primary task — *but* changes should be proposed in the plan phase with before/after text, not snuck into a diff.

4. **JSON data files.**
   `projects_data.json`, `reports.json` and any backup files are the only live data store right now. No destructive writes, no schema migrations, no bulk deletes. Never run a migration script unprompted.

---

## 10. Secrets, Config & Environment

### Required environment variables (current)
- `DEV_MODE=true` — enables the dev bypass in `backend/auth.py` and skips real token verification
- `VITE_DEV_MODE=true` — enables the dev token path in the frontend
- `ALLOWED_ORIGINS` — CORS whitelist, comma-separated (see [main.py](backend/main.py))
- `PORT` — server port (default 8000)

### Phase B will add
- Auth provider credentials (JWT secret, OAuth keys, etc.)
- Data store connection string
- LLM API key (Anthropic, OpenAI, or other — confirm with user before choosing)

### Sensitive data
- Financial data for real company projects. Treat all project names, revenue figures, and employee attendance as confidential.
- Don't paste real data into external tools (pastebins, diagram services, third-party AI) during debugging.
- The old `backend/service-account.json` (GCP key) no longer has any corresponding code — if found on disk it can be deleted.

---

## 11. Deployment

**Current state: not deployable to production.** Auth is stubbed; the app only works with `DEV_MODE=true`.

Phase B must complete auth + data store before a deployment pipeline is meaningful to build.

Once Phase B is done, the deployment target can be decided (the original plan was GCP Cloud Run, but that is now an open question since GCP dependencies were removed). Confirm with the user before picking a new hosting target.

### What's missing
- [ ] Phase B: real auth + data store + LLM (prerequisite for everything else)
- [ ] `docker-compose.yml` for local dev with live reload
- [ ] `cloudbuild.yaml` or equivalent CI/CD
- [ ] Health check endpoint (`/healthz`)
- [ ] Hosting target decision (Cloud Run, Railway, Render, Fly.io, etc.)

---

## 12. Known Gaps & Open Questions

Tracked here so Claude can raise them proactively when relevant:

1. **Phase B is the entire next milestone** — see §0 for the full stub list and task checklist.
2. **No test suite exists** despite the rule that changes should include tests. First-time-touched files should get tests added.
3. **No linter/formatter configured** despite the "full linting both sides" rule. Setup is a pending task.
4. **Deploy pipeline missing** — blocked on Phase B completing first.
5. **Legacy Excel/JSON artifacts** still referenced in [config.py](backend/config.py) and some services. The `*_firestore` function names in storage.py are misleading — they're JSON-only now. Phase B can rename them when replacing.
6. **Temporarily disabled features** (Attendance, Data upload) may come back — don't garbage-collect their integration points.
7. **Storage function naming** — `load_projects_firestore`, `save_project_firestore`, etc. in `storage.py` are misnamed after Phase A. Phase B should rename them when introducing the real data store.

---

## 13. Quick Reference

| Thing | Value |
|---|---|
| Brand | Logfi (internal codename: "סנג'ר של לנה") |
| Frontend | Vue 3.4 + Vite 5.4 + Tailwind 3.4 |
| Backend | FastAPI + Python 3.11 |
| Data store | **JSON files** (Phase B: TBD — PostgreSQL recommended) |
| Auth | **Stubbed** (Phase B: TBD) |
| LLM | **Stubbed** (Phase B: TBD) |
| Hosting target | **TBD** (GCP Cloud Run was original plan; now open) |
| Dev mode | `DEV_MODE=true` + `VITE_DEV_MODE=true` |
| Language (UI) | Hebrew, RTL |
| Language (Claude replies) | English |
| Currency | ₪ (ILS) |
| Default autonomy | Plan → approve → execute |
| Commit style | Descriptive multi-line (why > what) |
| Never touch without approval | Auth stub signatures, JSON data files, financial formulas, AI system prompts |
| Active branch | `claude/remove-gcp-dependencies-kAppr` |
