# CLAUDE.md — Logfi (IFMLogiX)

> Operating manual for Claude Code in this repo. Read this first, every session.
> Claude replies to the user in **English**. UI strings and user-facing text stay **Hebrew, RTL**.

---

## 1. Project Overview

**Logfi** (brand name: IFMLogiX, internal codename: "סנג'ר של לנה") is an internal financial dashboard for an Israeli FM (Facility Management) company. Its job is to give Lena and the management team real-time per-project visibility into P&L, cash flow, and risk.

**Core value (all four matter):**
1. **Per-project P&L visibility** — know which sites make or lose money, each month.
2. **Cash flow forecasting** — cumulative and monthly net liquidity view.
3. **Risk alerts / early warning** — surface projects bleeding margin before they become problems.
4. **AI CFO layer** — strategic direction; natural-language chat, automated risk scoring, what-if simulations. Currently stubbed — see §8.

**Users:** Lena + a management team of roughly 5–15 people. Mixed technical levels. Role-gated UI (see §5 Roles).

**Strategic scope:** Internal tool for **one company only**. Not SaaS, not multi-tenant. Do **not** introduce multi-tenant primitives without explicit approval.

**Language & UX:** Everything user-facing is Hebrew, RTL (`dir="rtl"`). All labels, errors, tooltips, chart legends. Code identifiers stay English.

---

## 2. Tech Stack

### Frontend ([frontend/package.json](frontend/package.json))
- **Vue 3.4** — Composition API + `<script setup>` exclusively. No Options API.
- **Vite 5.4** — dev server + build
- **Tailwind CSS 3.4** — utility classes; design tokens are CSS custom properties (see §6 Design)
- **Chart.js 4 + vue-chartjs 5** — all charts; shared config in `utils/chartDefaults.js`
- **Axios** — HTTP; all calls through `services/api.js`
- **html2pdf.js** — PDF export in ProjectDetailsView
- **marked** — Markdown rendering in AI chat
- **qrcode** — QR generation

### Backend ([backend/requirements.txt](backend/requirements.txt))
- **FastAPI + uvicorn[standard]** — API layer; serves built SPA in prod
- **psycopg[binary,pool]** — PostgreSQL via psycopg3; connection pool in `db.py`
- **PyJWT[crypto] + httpx** — Entra External ID JWT verification in `auth.py`
- **azure-identity + azure-keyvault-secrets** — Azure Key Vault for prod secrets
- **openpyxl + pandas** — Excel parsing for legacy import flows
- **python-multipart** — file uploads

### Runtime
- **Python 3.11** (Dockerfile)
- **Node 20** (Dockerfile frontend build stage)

---

## 3. Infrastructure Status

### Migration history (completed)
| Layer | Old (abandoned) | New (current) |
|---|---|---|
| Auth | Firebase Auth | Microsoft Entra External ID (backend JWT verified; frontend login still Phase 0 stub) |
| Database | Cloud Firestore | PostgreSQL (psycopg3 pool; schema in `backend/migrations/001_init.sql`) |
| Secrets | GCP Secret Manager | Azure Key Vault (`AZURE_KEY_VAULT_URL` + managed identity) |
| Hosting target | GCP Cloud Run | Azure Container Apps (not yet deployed — see §11) |

### GCP/Firebase status
**Completely abandoned.** The Firebase project `minlog-491211`, Cloud Firestore, Cloud Run, Vertex AI — none of this is in use or referenced. `.gitignore` retains legacy GCP credential patterns as a safeguard, not because they're active. Do not add any new GCP/Firebase dependencies.

### Current stub areas (not yet wired)
- **Frontend login** — Phase 0 stub. Any email+password submission stores a DEV token in localStorage and emits `login`. Real Entra OIDC flow is pending.
- **AI chat** — Phase 0 stub. `chat_stream()` in `ai_agents.py` emits a single placeholder SSE event. Azure OpenAI wiring is the planned next step.
- **Production deployment** — App runs locally only. No Azure Container Apps environment exists yet.

---

## 4. Repository Structure

```
proj-lena/
├── backend/
│   ├── main.py                    # FastAPI app; CORS, middleware, routers, SPA fallback
│   ├── auth.py                    # Entra External ID JWT verify; get_current_user dependency
│   ├── db.py                      # PostgreSQL connection pool (lazy; supports Azure Key Vault)
│   ├── storage.py                 # Persistence layer — PostgreSQL via psycopg3
│   │                              #   (functions keep _firestore suffix for call-site compat)
│   ├── middleware.py              # RequestLoggingMiddleware — structured JSON logs to stdout
│   ├── exception_handlers.py     # global_exception_handler — logs + 500 JSON response
│   ├── config.py                  # Legacy PROJECTS / EXPENSE_BREAKDOWN constants (pre-Postgres era)
│   ├── create_user.py             # Admin script for user setup
│   ├── create_test_projects.py    # Seed/demo data script
│   ├── migrations/
│   │   └── 001_init.sql           # Schema: users, projects (JSONB data column), reports
│   ├── routers/
│   │   ├── auth.py                # /api/auth/* — login stub, profile, user CRUD
│   │   ├── projects.py            # /api/projects/* — CRUD
│   │   ├── project_form.py        # /api/projects/form/* — wizard intake + actuals
│   │   ├── dashboard.py           # /api/dashboard/* — aggregated KPIs
│   │   ├── cashflow.py            # /api/cashflow/* — cumulative & monthly net
│   │   ├── reports.py             # /api/reports/* — spot reports
│   │   └── ai.py                  # /api/ai/* — chat stub, whatif, risk-scores
│   ├── services/
│   │   ├── unified.py             # Shared project data access layer
│   │   ├── form_calculator.py     # P&L math from form inputs (SENSITIVE — see §9)
│   │   ├── calculator_agent.py    # Risk scoring, what-if, budget-vs-actual (pure Python, no LLM)
│   │   ├── ai_agents.py           # SYSTEM_PROMPT + chat_stream stub; context builder
│   │   ├── excel_reader.py        # Legacy Excel import
│   │   └── payment_terms.py       # Payment schedule logic
│   ├── tests/
│   │   ├── conftest.py            # pytest fixtures: RSA key pair, Entra OIDC stubs, Postgres
│   │   ├── test_auth.py           # Auth JWT verification tests
│   │   └── test_storage.py        # Storage layer tests (requires DATABASE_URL)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue                # Top nav + tab router + role gating + toast host
│   │   ├── main.js                # Entry
│   │   ├── style.css              # Design tokens (CSS custom props), RTL base, global classes
│   │   ├── services/
│   │   │   └── api.js             # All HTTP calls + formatters (sole API surface)
│   │   ├── composables/
│   │   │   ├── useFocusTrap.js    # WCAG 2.1.2 keyboard trap for modals
│   │   │   └── useToast.js        # Toast notification provider/consumer
│   │   ├── utils/
│   │   │   └── chartDefaults.js   # COLORS token object + shared Chart.js plugin config
│   │   └── components/
│   │       ├── editorial/         # Design system primitives (see §6)
│   │       │   ├── index.js       # Named re-exports + currentHebrewDate()
│   │       │   ├── SectionHeader.vue
│   │       │   ├── RuledSection.vue
│   │       │   ├── HeroNumber.vue
│   │       │   ├── DataTable.vue
│   │       │   ├── PullQuote.vue
│   │       │   ├── SectionMarker.vue
│   │       │   ├── Dateline.vue
│   │       │   ├── FootnoteSource.vue
│   │       │   ├── EpigraphCaption.vue
│   │       │   └── SkeletonLoader.vue
│   │       ├── (29 page/feature components — see §6 for map)
│   │       └── ...
│   ├── vite.config.js             # Proxies /api → localhost:8000 in dev
│   ├── tailwind.config.js
│   └── package.json
├── Dockerfile                     # Multi-stage: Node build → Python 3.11 → uvicorn
├── CLAUDE.md                      # This file
└── (.gitignore covers: node_modules, dist, .env, *.xlsx, *.json data files, GCP creds)
```

**Temporarily disabled features:** `AttendanceView.vue`, `DataView.vue`, and their backend routers were removed but are on hold, not permanently gone. Do not delete references defensively; do not reintroduce without asking.

---

## 5. Architecture & Data Flow

### Database: PostgreSQL (canonical)

Schema lives in `backend/migrations/001_init.sql`. Three tables:

| Table | Key columns | Notes |
|---|---|---|
| `users` | `uid TEXT PK`, `email`, `full_name`, `role`, `linked_manager`, `avatar` | uid = Entra `oid` (or `dev-admin` in DEV_MODE) |
| `projects` | `id TEXT PK` (project name), hot cols (`manager`, `axis`, `area`, `status`, `source`), `data JSONB` | Full form payload in `data`; hot cols indexed |
| `reports` | `id SERIAL`, `project_id → projects.id`, `month`, `type`, `title`, `amount` | Cascading delete on project removal |

Apply schema: `psql "$DATABASE_URL" -f backend/migrations/001_init.sql`

`storage.py` function names retain `_firestore` suffix for call-site compatibility — this is intentional and will be renamed in a later pass.

**Do not** treat any local JSON files as the source of truth. The hardcoded `PROJECTS`/`EXPENSE_BREAKDOWN` dicts in `config.py` are legacy Excel-era constants — check whether any feature should be pulling from Postgres before relying on them.

### Auth

**Backend** (`auth.py`): Entra External ID RS256 JWT verification. Flow:
1. Extract bearer token from `Authorization` header.
2. If `DEV_MODE=true` and token is `dev-admin-local`, short-circuit to admin user.
3. Otherwise: decode JWT header, look up `kid` in JWKS cache (fetched from OIDC discovery), verify signature via PyJWT.
4. Extract `oid` as `uid`; `preferred_username` / `email` for email.
5. Merge role, `linked_manager`, `full_name` from `users` table (not from token claims). First-time logins auto-insert a `viewer` row.

**Frontend** (`LoginPage.vue`): Phase 0 stub. Email+password form that stores the DEV token in `localStorage` and emits `login`. No real Entra OIDC flow yet. `api.js` reads `auth_token` from localStorage and sets `Authorization: Bearer <token>`.

**Roles** (four, exhaustive):

| Role | Hebrew label | Access |
|---|---|---|
| `admin` | מנהל מערכת | Full access; settings; user management |
| `economist` | כלכלנית | Same edit rights as admin; no user management |
| `viewer` | צופה מלא | Read-only; default on first login |
| `project_manager` | מנהל פרויקט | Sees only assigned projects (My Projects view) |

`isAdmin` = `role === 'admin'`. `isEditor` = `['admin', 'economist'].includes(role)`.

### AI layer

**Status: fully stubbed.** No LLM is connected.

- `chat_stream()` in `ai_agents.py` emits one placeholder SSE event and returns.
- `SYSTEM_PROMPT` and the context builder are preserved and model-agnostic — ready to wire to Azure OpenAI.
- `calculator_agent.py` (what-if simulation, risk scores, budget-vs-actual) runs **pure Python math** — no LLM dependency, fully functional.

When the AI wiring task comes: confirm with the user before adding any LLM SDK dependency. Likely target is Azure OpenAI via `openai` SDK (not `anthropic` or `google-genai`).

**Frontend UI components** (AiChat.vue, WhatIfPanel.vue, RiskScoreBadge.vue) are fully built and accessible. They surface the stub responses correctly.

### API conventions
- All routes under `/api/`. Health check at `GET /api/health`.
- Response shapes follow the existing router's pattern. Add to the same pattern when extending.
- Error messages via `HTTPException` **in Hebrew**: `raise HTTPException(status_code=404, detail="פרויקט לא נמצא")`.
- All frontend HTTP calls go through `frontend/src/services/api.js`. Never `axios.get` directly from components.

### State management
- No Pinia, no Vuex. Component-local `ref()` + `computed()`.
- `activeTab` ref in `App.vue` controls which page renders. No Vue Router — open to introducing it if there's a clear reason, but don't migrate for its own sake.
- Cross-component state passes via props or re-fetches from the API.

---

## 6. Code Style & Conventions

### Hard rules (violating these is a bug)
- **Hebrew UI, English code.** Every user-visible string in Hebrew. Every identifier, comment, log line in English.
- **Composition API only.** No `<script>` Options API blocks.
- **Financial values in ₪ (ILS).** Use `formatNumber` from `api.js`. Months are 1–12.
- **RTL everywhere.** Root has `dir="rtl"`; Chart.js tooltips need `{ rtl: true, cornerRadius: 12 }`.
- **Revenue forecasts must sum to 100%** (percentage-based in the project form).
- **All colors via design tokens** — `var(--*)` in CSS/templates; `COLORS.*` from `chartDefaults.js` in JS Chart.js config. Never hardcode hex in component styles.

### Design system

The design system is editorial/typographic — **not** glassmorphic, not iOS-inspired. The old `.ios-card` description is obsolete.

**CSS tokens** (defined in `style.css` as custom properties):

| Token group | Key tokens |
|---|---|
| Surface | `--surface`, `--surface-muted`, `--bg` |
| Ink | `--ink`, `--ink-strong`, `--ink-muted`, `--ink-faint`, `--ink-whisper` |
| Border | `--border`, `--border-strong` |
| Accent | `--accent`, `--accent-hover`, `--accent-soft` |
| Semantic | `--positive`, `--positive-soft`, `--negative`, `--negative-soft`, `--warning`, `--warning-soft`, `--info` |
| Radius | `--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-xl` |
| Shadow | `--shadow-sm`, `--shadow-md`, `--shadow-xl` |
| Motion | `--ease-out`, `--dur-press` |

**Chart.js color tokens** — import `COLORS` from `src/utils/chartDefaults.js`. Never use raw hex strings for chart datasets. Key values: `COLORS.accent`, `COLORS.emerald`, `COLORS.cyan`, `COLORS.purple`, `COLORS.amber`, `COLORS.amberFill`, `COLORS.amberLight`, `COLORS.paperLight`.

**Editorial component library** — import from `./editorial` (the `index.js` barrel):
- `SectionHeader` — page-level title block with eyebrow, kicker, subtitle, actions slot. Accepts `level` prop (default 2) for heading level.
- `RuledSection` — titled section with ruled separator, footnote slot.
- `HeroNumber` — large KPI display with tone, prefix, footnote.
- `DataTable` — sortable, searchable, paginated table with custom cell slots.
- `PullQuote` — callout with semantic variants (negative, warning, info).
- `SectionMarker` — tab-bar navigation component.
- `SkeletonLoader` — loading placeholders (variants: kpi, chart, cards).
- `FootnoteSource`, `Dateline`, `EpigraphCaption` — typography utilities.
- `currentHebrewDate()` — utility: current month in Hebrew, e.g. "מאי 2026".

**Composables** (`src/composables/`):
- `useFocusTrap(containerRef)` — activate/deactivate keyboard trap for modals. Always use on modal-like surfaces. Returns `{ activate, deactivate }`. Wire via `watch(show, async val => { if (val) { await nextTick(); activate() } else { deactivate() } })`.
- `useToast()` — `{ success(msg), error(msg), info(msg) }`. Provider in `App.vue`; inject with `useToast()` in any component.

**Accessibility — WCAG 2.1 AA compliant.** All forms have `for`/`id` label/input pairs. All modals use `useFocusTrap`. All decorative SVGs have `aria-hidden="true"`. Icon-only buttons have `aria-label`. The AI chat message list has `aria-live="polite"`. `sr-only` h1 landmarks on Dashboard and ExecutiveDashboard. Do not regress these.

**Banned patterns** (enforced by `/impeccable` design system):
- Side-stripe borders: no `border-left/right > 1px` as colored accents on cards or alerts
- Gradient text: no `background-clip: text`
- Glassmorphism: no decorative blurs
- Layout property animations: use `transform` + `scaleX()` instead of animating `width`/`height`
- Hardcoded hex in component styles: always use `var(--*)` or `COLORS.*`

### Component map (29 main + 10 editorial)

**Pages / views:** `Dashboard.vue`, `ExecutiveDashboard.vue`, `PnlView.vue`, `CashFlowView.vue`, `AlertsView.vue`, `MyProjectsView.vue`, `ProjectDetailsView.vue`, `ProjectFormDashboard.vue`, `LoginPage.vue`

**Feature panels:** `AiChat.vue`, `WhatIfPanel.vue`, `MonthlyActualsEditor.vue`

**Modals:** `ProjectFormModal.vue`, `SettingsModal.vue`, `UserProfileModal.vue`, `ReportModal.vue`

**Charts:** `PnlChart.vue`, `CashFlowChart.vue`, `RevenueExpenseChart.vue`, `MonthlyNetChart.vue`, `ProjectNetChart.vue`, `CashflowMiniChart.vue`, `ProjectCashflowChart.vue`, `ProjectCompareChart.vue`, `ProfitBarChart.vue`, `ExpenseBreakdown.vue`

**Atoms:** `DatePicker.vue`, `RiskScoreBadge.vue`

### Linting & formatting
Not yet configured. If asked to set it up:
- Frontend: ESLint flat config + Prettier, `lint` and `format` npm scripts.
- Backend: Ruff (lint + format).
- Do **not** silently auto-lint unrelated files alongside a feature change.

### Naming
- Components: `PascalCase.vue`
- JS services/composables/utils: `camelCase.js`
- Python modules: `snake_case.py`
- API endpoints: `/api/resource/verb` kebab-case

### Recipes

**New page:**
1. Create SFC in `frontend/src/components/`
2. Import as `defineAsyncComponent` in `App.vue`
3. Add `activeTab` case and role gate
4. Fetch data via `api.js`
5. Add `<h1 class="sr-only">…</h1>` as first element for SR page landmark

**New API endpoint:**
1. Route in appropriate `backend/routers/*.py`
2. `Depends(get_current_user)` on anything non-public
3. Export from `api.js`
4. Hebrew `HTTPException` detail

**New chart:**
1. vue-chartjs component, register ChartJS modules at top
2. Import `COLORS` and `chartDefaults` from `utils/chartDefaults.js`
3. RTL tooltip: `{ rtl: true, cornerRadius: 12 }`

**New modal:**
1. `ref="modalCard"` on the card element
2. Import and wire `useFocusTrap(modalCard)` with `watch(show, ...)`
3. All inputs must have `for`/`id` label associations
4. Close button needs `aria-label="סגור"`

---

## 7. How Claude Works in This Repo

### Autonomy: **plan first, then execute**
For any non-trivial change:
1. Read enough code to understand the real state (don't guess).
2. Produce a plan: files to touch, exact changes, risks, verification steps.
3. Wait for approval.
4. Execute. Report back.

Trivial fixes (typos, obvious one-liners, answering questions) don't need a formal plan.

### When uncertain: **research more, then decide**
Don't ask the user a question you could answer by reading 3 more files. Grep, read, verify — then either proceed with confidence or come back with 2–3 concrete options and a recommendation.

### Communication style
- Reply in **English**. UI strings in Hebrew.
- Terse action-first for small tasks; step-by-step reasoning for complex/risky changes.
- No trailing summary of obvious diffs. The user reads diffs.
- Lead with the answer or action.

### Commits
```
Short imperative title (<72 chars)

Body explaining the why: what problem this solves, what the user
was seeing, and any non-obvious tradeoffs. Reference files if it
helps future readers navigate.
```
Never commit unless the user asks. Never `--amend` without being told.

### Primary task mix (rough frequency order)
1. **Azure deployment pipeline** — the explicit next priority: Container Apps config, CI/CD
2. **Frontend Entra login** — replace Phase 0 stub with real OIDC flow
3. **AI chat wiring** — connect Azure OpenAI to the existing stub infrastructure
4. **New features** — dashboard views, role flows
5. **Bug fixes** — across any area

---

## 8. Current Hot Zones (in flux — treat with care)

1. **Auth stub → real Entra flow.** `LoginPage.vue` is a stub. `auth.py` is ready for production JWT verification but depends on `ENTRA_*` env vars. Any change to the login flow needs coordination across both.

2. **AI features.** `ai_agents.py` `chat_stream()` is a stub. `calculator_agent.py` (risk scoring, what-if) is functional pure-Python. When wiring Azure OpenAI, touch only `ai_agents.py` — do not touch calculator logic.

3. **Financial calculations.** `form_calculator.py` and the P&L math in `calculator_agent.py` drive every dashboard number. Small changes ripple everywhere. See §9.

4. **storage.py function naming.** Functions keep `_firestore` suffix intentionally (call-site compat). A rename pass is planned — don't do it opportunistically alongside feature work.

---

## 9. Do Not Touch Without Explicit Approval

1. **Auth configuration.** `auth.py`, the login flow in `LoginPage.vue`, any Entra app registration settings. Breaking auth locks everyone out.

2. **Database schema / data.** No destructive writes, no schema changes, no migration scripts unprompted. Read freely; write only through normal app code paths.

3. **Financial calculation formulas.** `form_calculator.py`, P&L and margin math in `calculator_agent.py`. These drive management decisions and the user has been burned by silent formula changes. Reading is fine; changing requires the user to explicitly say "edit the formula" and review the diff line-by-line.

4. **AI system prompts.** `SYSTEM_PROMPT` and context-builder in `ai_agents.py`. Propose before/after text in the plan phase — don't change in a diff without prior review.

---

## 10. Secrets, Config & Environment

### Expected environment variables

**Local dev** (put in `backend/.env`):
```
DEV_MODE=true
DATABASE_URL=postgresql://user:pass@localhost:5432/logfi
ALLOWED_ORIGINS=http://localhost:3000
```

**Production (Azure Container Apps)**:
```
ENTRA_TENANT_ID=<tenant-guid>
ENTRA_CLIENT_ID=<app-registration-guid>
ENTRA_AUTHORITY=https://<tenant>.ciamlogin.com   # Entra External ID
AZURE_KEY_VAULT_URL=https://<vault>.vault.azure.net
POSTGRES_SECRET_NAME=POSTGRES-CONN               # default; Key Vault secret name
ALLOWED_ORIGINS=https://app.example.com
PORT=8080                                         # Azure Container Apps injects this
```

When `AZURE_KEY_VAULT_URL` is set, `db.py` fetches the Postgres connection string from Key Vault via managed identity — no key file in the container.

### DEV_MODE
When `DEV_MODE=true`, `auth.py` accepts the token string `dev-admin-local` and maps it to a hardcoded admin user. The frontend Phase 0 stub always sends this token. Never enable DEV_MODE in production.

### Sensitive data
Financial data for real company projects. Treat all project names, revenue figures, and employee data as confidential. Don't paste into external tools (pastebins, diagram services, third-party AI).

---

## 11. Deployment (Target: Azure Container Apps)

**Current state: not deployed.** The app runs locally only. The `Dockerfile` is production-ready (multi-stage: Vite build → Python 3.11 image → uvicorn). No cloud environment exists yet.

The user's stated next priority is deploying to Azure Container Apps.

### Target architecture
- **Azure Container Apps** — single container running the multi-stage `Dockerfile` (FastAPI + bundled SPA)
- **Azure Database for PostgreSQL** — managed Postgres, connected via `POSTGRES-CONN` secret in Key Vault
- **Azure Key Vault** — all backend secrets; accessed via managed identity (no key files in container)
- **Microsoft Entra External ID** — auth provider (backend JWT verification ready; frontend login pending)
- **Azure Container Registry** — image registry
- **Region:** confirm with user. `swedencentral` or `westeurope` are low-latency options for Israel.

### What's missing
- [ ] Azure Container Apps environment + Container App resource
- [ ] Azure Container Registry push + image tagging
- [ ] CI/CD pipeline (GitHub Actions or Azure DevOps) triggering on push to `main`
- [ ] Azure Database for PostgreSQL provisioned + schema applied
- [ ] Key Vault with `POSTGRES-CONN` secret
- [ ] Managed identity bound to Container App with Key Vault + DB access
- [ ] Frontend Entra login (OIDC flow replacing the stub)
- [ ] `docker-compose.yml` for local dev with live reload (separate from prod `Dockerfile`)

### Environments
No formal dev/staging/prod split exists. Recommend Option A for an internal 5–15 user tool: `main` → single prod Container App; local Docker for dev.

---

## 12. Testing

### Backend (works)
```bash
cd backend
pip install -r requirements.txt pytest cryptography
pytest tests/
```
- `test_auth.py` — RS256 JWT verification; Entra OIDC discovery + JWKS stubbed via monkeypatch
- `test_storage.py` — Postgres CRUD; requires `DATABASE_URL` env var; skips gracefully if missing

Fixtures in `conftest.py` generate a real RSA-2048 key pair per session and stub OIDC HTTP calls.

### Frontend (not configured)
No Vitest setup exists yet. First-time-touched components should get tests added. When setting up:
- Vitest + `@vue/test-utils` + `jsdom`
- Add `test` script to `package.json`
- Priority: form validation logic, financial formatters in `api.js`

Until a frontend runner is configured, every plan must include a **manual verification checklist**.

---

## 13. Known Gaps & Open Tasks

1. **Frontend Entra login** — `LoginPage.vue` is a stub. Real OIDC flow needs MSAL or a redirect-based Entra flow.
2. **AI chat wiring** — `chat_stream()` is a stub. Wire to Azure OpenAI when the CIO confirms the tenant.
3. **No deploy pipeline** — highest-priority infrastructure task. See §11.
4. **No frontend test runner** — Vitest not configured. Add alongside the next significant component change.
5. **No linter/formatter** — ESLint + Prettier (frontend), Ruff (backend) pending.
6. **`storage.py` `_firestore` naming** — planned rename pass; don't rename opportunistically.
7. **`config.py` legacy constants** — `PROJECTS` / `EXPENSE_BREAKDOWN` are pre-Postgres era. Any new feature should read from Postgres via `unified.py`, not from these dicts.
8. **Temporarily disabled features** — `AttendanceView.vue`, `DataView.vue`, and their routers are on hold. Don't garbage-collect their integration points.

---

## 14. Quick Reference

| Thing | Value |
|---|---|
| Brand | IFMLogiX (internal codename: Logfi / "סנג'ר של לנה") |
| Frontend | Vue 3.4 + Vite 5.4 + Tailwind 3.4 |
| Backend | FastAPI + Python 3.11 |
| Database | PostgreSQL (psycopg3); schema in `backend/migrations/001_init.sql` |
| Auth | Entra External ID (backend ready; frontend login = Phase 0 stub) |
| AI / LLM | Stub only — no LLM connected. Calculator math works. |
| Hosting target | Azure Container Apps (not yet deployed) |
| Secrets (prod) | Azure Key Vault via managed identity |
| Language (UI) | Hebrew, RTL |
| Language (Claude) | English |
| Currency | ₪ (ILS) |
| Roles | admin, economist, viewer, project_manager |
| Design system | Editorial/typographic; CSS custom props (`var(--*)`); editorial component library |
| Accessibility | WCAG 2.1 AA compliant — do not regress |
| Default autonomy | Plan → approve → execute |
| Commit style | Descriptive multi-line (why > what) |
| Never touch without approval | Auth config, DB schema/data, financial formulas, AI prompts |
| Top priority | Deploy to Azure Container Apps |
