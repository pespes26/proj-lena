# CLAUDE.md — Logfi (FM Financial Co-Pilot)

> Operating manual for Claude Code in this repo. Read this first, every session.
> Claude replies to the user in **English**. UI strings and user-facing text stay **Hebrew, RTL**.

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
- **Firebase 12.11** — Auth (client SDK; see [firebase.js](frontend/src/firebase.js), project `minlog-491211`)
- **Axios** — HTTP
- **html2pdf.js** — PDF export
- **marked** — Markdown rendering (used in AI chat responses)
- **qrcode** — QR generation

### Backend ([backend/requirements.txt](backend/requirements.txt))
- **FastAPI + uvicorn[standard]** — API layer, also serves built frontend SPA in prod
- **firebase-admin** — backend token verification (see [backend/auth.py](backend/auth.py))
- **google-cloud-firestore** — primary data store
- **google-cloud-storage** — file/backup storage
- **google-genai** — **primary LLM SDK (Vertex AI Gemini)**
- **anthropic** — also present in requirements; Claude may be used as secondary model. Confirm with user before introducing new Anthropic calls.
- **openpyxl + pandas** — Excel parsing for legacy/import flows
- **python-multipart** — file uploads

### Runtime
- **Python 3.11** (see [Dockerfile](Dockerfile))
- **Node 20** (Dockerfile frontend build stage)

---

## 3. Repository Structure

```
Lena/
├── backend/
│   ├── main.py                    # FastAPI entrypoint; mounts SPA from frontend/dist in prod
│   ├── auth.py                    # Firebase token verification, get_current_user dependency
│   ├── config.py                  # Hardcoded PROJECTS, month maps, expense breakdowns, file paths
│   ├── storage.py                 # Firestore/JSON persistence helpers
│   ├── create_user.py             # Admin script for user setup
│   ├── create_test_projects.py    # Seed/demo data script
│   ├── routers/
│   │   ├── auth.py                # /api/auth/* — login, user profile
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
│   │   ├── ai_agents.py           # LLM system prompt, chat_stream, context builder
│   │   ├── excel_reader.py        # Legacy Excel import
│   │   └── payment_terms.py       # Payment schedule logic
│   ├── service-account.json       # GCP SA key (local dev only — MUST be gitignored, see §10)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue                # Top nav + tab router + role gating
│   │   ├── main.js                # Entry
│   │   ├── firebase.js            # Firebase client init (project minlog-491211)
│   │   ├── style.css              # Global tokens, RTL base
│   │   ├── services/api.js        # All HTTP calls + formatters (single source of truth for API surface)
│   │   └── components/            # 28 Vue SFCs (pages, charts, modals)
│   ├── vite.config.js             # Proxies /api → localhost:8000 in dev
│   ├── tailwind.config.js
│   └── package.json
├── Dockerfile                     # Multi-stage: build frontend → bundle into Python image → uvicorn
├── CLAUDE.md                      # This file
└── (data.xlsx, *.json, backups/, contracts/)    # Gitignored data artifacts
```

**Notable currently-disabled features:** `AttendanceView.vue`, `DataView.vue`, `routers/attendance.py`, `routers/data.py` were removed but are **temporarily disabled**, not permanently gone. Do not delete references defensively; do not reintroduce them without asking.

---

## 4. Running the App

### Day-to-day local dev: **Docker**
The user runs the app via Docker locally. A production [Dockerfile](Dockerfile) exists (multi-stage: builds Vue frontend, copies into a Python 3.11 image, runs uvicorn serving both API and static SPA).

**Gap Claude may be asked to fix:** there is no `docker-compose.yml` yet for local dev with live reload. If asked to set one up, propose: one service for backend (uvicorn with `--reload`), one for frontend (vite dev server), shared volume for source, proxied via vite. Ask before creating.

### Fallback — bare metal
```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (separate terminal)
cd frontend && npm install && npm run dev
```
Vite dev server runs on port 3000 and proxies `/api/*` → `localhost:8000`.

### Build for production
```bash
docker build -t logfi .
docker run -p 8000:8000 --env-file .env logfi
```
In production the FastAPI app serves the built SPA at `/` and catches all non-`/api` routes via [main.py:33](backend/main.py#L33).

### Tests
**Stated rule:** a full test suite is required for changes.
**Current reality:** no test suite exists yet in the repo. This is a **gap**, not a settled state. When Claude makes non-trivial changes, it should:
1. Propose adding tests (pytest for backend, Vitest for frontend) alongside the change.
2. For touched financial/AI logic, prioritize writing tests *even if* the surrounding area is untested.
3. When the user explicitly says "skip tests," respect that — but note it in the plan.

Until a test runner is configured, every plan must include a **manual verification checklist** the user can click through.

---

## 5. Architecture & Data Flow

### Data store: **Firestore (canonical)**
All persistent data lives in **Cloud Firestore** (project `minlog-491211`). Excel and JSON files in the repo (`data.xlsx`, `projects_data.json`, `reports.json`, `attendance_data.json`) are either:
- legacy artifacts from the pre-Firebase era, or
- import sources used by one-off scripts.

**Do not** treat local JSON files as the source of truth. **Do not** write new features that read/write those files unless explicitly migrating. When in doubt, read from Firestore via [backend/storage.py](backend/storage.py) and [backend/services/unified.py](backend/services/unified.py).

The hardcoded `PROJECTS` / `EXPENSE_BREAKDOWN` dicts in [backend/config.py](backend/config.py) are also legacy Excel-era constants. Check whether a feature should be pulling from Firestore instead before relying on them.

### Auth
- **Frontend:** Firebase Auth via [firebase.js](frontend/src/firebase.js). Login flow in [LoginPage.vue](frontend/src/components/LoginPage.vue). ID token attached to API requests.
- **Backend:** [backend/auth.py](backend/auth.py) verifies tokens with `firebase-admin`. All protected routers use `Depends(get_current_user)` — see [backend/routers/ai.py:9](backend/routers/ai.py#L9) as reference.
- **Roles:** at least `admin` and `project_manager` (checked in [App.vue](frontend/src/App.vue) for tab gating). More may exist — grep before assuming.

### AI layer ([backend/services/ai_agents.py](backend/services/ai_agents.py), [backend/services/calculator_agent.py](backend/services/calculator_agent.py))
- **Primary model:** Google Vertex AI Gemini via `google-genai` SDK.
- **Endpoints** (all under [backend/routers/ai.py](backend/routers/ai.py)):
  - `POST /api/ai/chat` — streaming chat (SSE) over project context
  - `POST /api/ai/whatif` — scenario simulation for a project
  - `GET /api/ai/risk-scores` — all projects
  - `GET /api/ai/risk-score/{project}` — single project
- **Frontend UI:** [AiChat.vue](frontend/src/components/AiChat.vue), [WhatIfPanel.vue](frontend/src/components/WhatIfPanel.vue), [RiskScoreBadge.vue](frontend/src/components/RiskScoreBadge.vue), [ExecutiveDashboard.vue](frontend/src/components/ExecutiveDashboard.vue).
- **Prompts live in code.** `SYSTEM_PROMPT` and context-building functions are in `ai_agents.py`. See §9 before editing prompts.

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
1. **New features** — AI-driven, dashboard views, role flows
2. **AI prompt & agent tuning** — improving [ai_agents.py](backend/services/ai_agents.py) prompts, tool definitions, context building
3. **Bug fixes** — across any area

Refactors are welcome but should be explicit and scoped, never snuck in alongside feature work.

---

## 8. Current Hot Zones (in flux — treat with care)

These areas are actively changing and more likely to have rough edges. Read carefully before editing.

1. **Financial calculations** — [backend/services/form_calculator.py](backend/services/form_calculator.py), [backend/services/calculator_agent.py](backend/services/calculator_agent.py). Small changes to P&L math ripple into every dashboard number and every AI risk score. See §9.
2. **AI features** — The whole AI stack is new: [routers/ai.py](backend/routers/ai.py), [services/ai_agents.py](backend/services/ai_agents.py), and the frontend components [AiChat.vue](frontend/src/components/AiChat.vue), [WhatIfPanel.vue](frontend/src/components/WhatIfPanel.vue), [RiskScoreBadge.vue](frontend/src/components/RiskScoreBadge.vue), [ExecutiveDashboard.vue](frontend/src/components/ExecutiveDashboard.vue). Expect churn. Prompts and tool signatures may change between sessions.
3. **Auth / user management** — Firebase migration is recent; role semantics (`admin`, `project_manager`, possibly more) are still settling. Check [backend/auth.py](backend/auth.py) and the role checks in [App.vue](frontend/src/App.vue) before assuming.

---

## 9. Do Not Touch Without Explicit Approval

These areas are **locked** by default. If a task seems to require touching them, stop and ask.

1. **Auth / Firebase configuration.**
   [frontend/src/firebase.js](frontend/src/firebase.js), [backend/auth.py](backend/auth.py), Firebase console settings, security rules, the login flow in [LoginPage.vue](frontend/src/components/LoginPage.vue). Breaking auth locks everyone out.

2. **Firestore data & backups.**
   No destructive writes, no schema migrations, no "cleanup" scripts, no bulk deletes. Read freely; write only through normal app code paths that the user is testing end-to-end. Never run a migration script unprompted. Never delete a backup.

3. **Financial calculation formulas.**
   `form_calculator.py`, the P&L math in `calculator_agent.py`, revenue/expense aggregation, margin calculations. Reason: these numbers drive management decisions and the user has been burned by silent formula changes. Reading is fine; changing requires the user to explicitly say "edit the formula" and review the diff line-by-line.

4. **AI system prompts.**
   The `SYSTEM_PROMPT` and context-builder in [backend/services/ai_agents.py](backend/services/ai_agents.py) shape what the AI CFO says to the user. Prompt tuning is a primary task — *but* changes should be proposed in the plan phase with before/after text, not snuck into a diff.

---

## 10. Secrets, Config & Environment

### Where secrets live today
- **Local dev:** `.env` files (gitignored) + `backend/service-account.json` (GCP SA key)
- **Production target:** **GCP Secret Manager** for backend secrets, Firebase config baked into the frontend bundle (Firebase client keys are not secrets — they're scoped by security rules)

### service-account.json — current status & recommendation
The file `backend/service-account.json` is currently present as an untracked file. **Gitignore gap:** [.gitignore](.gitignore) blocks `backend/firebase-service-account.json` and `*firebase-adminsdk*.json` but **does not block the exact filename `service-account.json`**. First action if Claude is asked to help with secrets: add `backend/service-account.json` and `**/service-account*.json` to `.gitignore`. Verify the file has never been committed (`git log --all --full-history -- backend/service-account.json`).

**Recommended long-term pattern** (ask the user before implementing):
- **Local dev:** keep `service-account.json` on disk, export `GOOGLE_APPLICATION_CREDENTIALS=/app/backend/service-account.json`. Never commit.
- **Cloud Run:** attach a dedicated runtime service account with IAM roles for Vertex AI, Firestore, Cloud Storage, and Secret Manager. **No key file needed in the container** — the ADC (Application Default Credentials) flow picks up the runtime SA automatically. This is the GCP-native pattern and eliminates the key-leak risk entirely.

### Expected environment variables
Based on code inspection:
- `ALLOWED_ORIGINS` — CORS whitelist, comma-separated (see [main.py:8](backend/main.py#L8))
- `PORT` — server port (Cloud Run injects this; default 8000)
- `GOOGLE_APPLICATION_CREDENTIALS` — path to SA key for local dev
- Firebase admin and Vertex/google-genai will pick up credentials via ADC; no explicit vars if ADC is configured
- Likely also: Firebase project ID, Gemini model name, any Anthropic API key if Claude is being called. Confirm by reading [backend/services/ai_agents.py](backend/services/ai_agents.py) when in doubt.

### Sensitive data
- Financial data for real company projects. Treat all project names, revenue figures, and employee attendance as confidential.
- Don't paste real data into external tools (pastebins, diagram services, third-party AI) during debugging.

---

## 11. Deployment (Target: GCP Cloud Run)

**Current state: no working deploy pipeline.** The user said explicitly: *"I don't deploy it properly yet and I should do it."* This is an open area Claude is expected to help design when asked.

### Target architecture
- **Cloud Run** — single service running the multi-stage [Dockerfile](Dockerfile) (FastAPI serving API + bundled frontend SPA)
- **Vertex AI (Gemini)** — LLM via `google-genai` SDK, authenticated via Cloud Run runtime SA
- **Firebase** — Auth + Firestore (project `minlog-491211`)
- **Secret Manager** — backend secrets (any API keys, webhook URLs, etc.)
- **Cloud Build** — CI/CD trigger on `git push` to `main`
- **Region:** confirm with user before first deploy. Common choice for Israel is `europe-west1` (Belgium) or `europe-west4` (Netherlands) — lowest latency, Vertex + Firestore both supported. Avoid US regions unless there's a reason.

### What's missing (tasks Claude may be asked to do)
- [ ] `cloudbuild.yaml` at repo root — build image, push to Artifact Registry, deploy to Cloud Run
- [ ] Cloud Build trigger wired to the GitHub repo
- [ ] Runtime service account with minimal IAM (`roles/aiplatform.user`, `roles/datastore.user`, `roles/storage.objectUser`, `roles/secretmanager.secretAccessor`)
- [ ] Secret Manager entries for any backend API keys, wired into Cloud Run env
- [ ] `docker-compose.yml` for local dev (separate from prod Dockerfile)
- [ ] Health check endpoint (`/healthz`) if not already present

### Environments
**Current state: no formal dev/staging/prod split.** Whatever is in `main` is "the app." When setting up deploy, recommend to the user:
- **Option A (simple):** `main` → prod Cloud Run; ephemeral local Docker for dev. One environment.
- **Option B (safer):** `main` → staging Cloud Run, tagged releases → prod Cloud Run. Two Firestore projects (or one project with environment-prefixed collections).

Option A is probably right for an internal tool with 5–15 users. Confirm before building infrastructure.

---

## 12. Known Gaps & Open Questions

Tracked here so Claude can raise them proactively when relevant:

1. **No test suite exists** despite the rule that changes should include tests. First-time-touched files should get tests added.
2. **No linter/formatter configured** despite the "full linting both sides" rule. Setup is a pending task.
3. **Deploy pipeline missing** — see §11.
4. **`service-account.json` gitignore gap** — see §10.
5. **Legacy Excel/JSON artifacts** still referenced in [config.py](backend/config.py) and some services even though Firestore is canonical. Migration isn't finished; watch for dual code paths.
6. **Temporarily disabled features** (Attendance, Data upload) may come back — don't garbage-collect their integration points.
7. **Dual LLM SDKs** (`google-genai` and `anthropic`) in requirements. Primary is Vertex Gemini; confirm before adding new Anthropic call sites.

---

## 13. Quick Reference

| Thing | Value |
|---|---|
| Brand | Logfi (internal codename: "סנג'ר של לנה") |
| Frontend | Vue 3.4 + Vite 5.4 + Tailwind 3.4 |
| Backend | FastAPI + Python 3.11 |
| Data store | Cloud Firestore (`minlog-491211`) |
| Auth | Firebase Auth |
| LLM | Vertex AI Gemini (primary) |
| Hosting target | GCP Cloud Run |
| Language (UI) | Hebrew, RTL |
| Language (Claude replies) | English |
| Currency | ₪ (ILS) |
| Default autonomy | Plan → approve → execute |
| Commit style | Descriptive multi-line (why > what) |
| Never touch without approval | Auth, Firestore data, financial formulas, AI system prompts |
