# IFMLogiX

IFMLogiX is a financial management platform built for Logi Group, providing P&L tracking, cash flow analysis, and AI-assisted reporting across projects. The system is deployed on Google Cloud Platform (GCP) and accessible via Firebase Hosting backed by Cloud Run.

---

## Architecture

| Layer | Technology |
|---|---|
| Frontend | Vue 3 (served from `frontend/dist`) |
| Backend | FastAPI (Python 3.11) |
| Authentication | Firebase Auth (ID token verification) |
| Database | Firestore |
| AI | Gemini AI (`/api/ai/chat`) |
| Hosting | Firebase Hosting + Cloud Run (`logfi`, `europe-west1`) |
| Container | Docker (multi-stage: Node 20 build → Python 3.11 runtime) |

---

## Roles

| Role | Description |
|---|---|
| `admin` | Full system access — user management, all data, all settings |
| `economist` | Can create and edit all financial data across all projects |
| `viewer` | Read-only access to all projects and reports |
| `project_manager` | Can edit data only for projects they are linked to |

Roles are stored per user in Firestore (`users/{uid}.role`). First-time logins default to `viewer`.

---

## Local Development

### Backend

```bash
cd backend
cp .env.example .env   # fill in GEMINI_API_KEY, ALLOWED_ORIGINS
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dev server will be available at `http://localhost:3000`.

> The backend reads `ALLOWED_ORIGINS` from the environment and allows `http://localhost:3000` by default, so CORS is pre-configured for local development.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | API key for Gemini AI (Google AI Studio) |
| `ALLOWED_ORIGINS` | Yes | Comma-separated list of allowed CORS origins (e.g. `https://your-domain.com`) |
| `GOOGLE_APPLICATION_CREDENTIALS` | In some envs | Path to GCP service account JSON. Not needed on Cloud Run (uses attached service account). |

On Cloud Run, Firebase Admin SDK uses the attached service account automatically — no credentials file is required.

---

## Deploy

### Cloud Run

```bash
# Build and push image
docker build -t gcr.io/<PROJECT_ID>/logfi .
docker push gcr.io/<PROJECT_ID>/logfi

# Deploy to Cloud Run
gcloud run deploy logfi \
  --image gcr.io/<PROJECT_ID>/logfi \
  --region europe-west1 \
  --platform managed \
  --set-env-vars GEMINI_API_KEY=<key>,ALLOWED_ORIGINS=<origin>
```

### Firebase Hosting

```bash
cd frontend
npm run build
firebase deploy --only hosting
```

Firebase Hosting rewrites all traffic to the `logfi` Cloud Run service in `europe-west1` (see `firebase.json`).

---

## Key Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Health check — returns `{"status": "ok"}` |
| `GET` | `/api/auth/profile` | Returns the authenticated user's profile and role |
| `GET/POST` | `/api/projects` | List or create projects |
| `GET` | `/api/dashboard` | Aggregated dashboard data |
| `POST` | `/api/ai/chat` | Send a message to the Gemini AI assistant |

All endpoints (except `/api/health`) require a Firebase ID token passed as `Authorization: Bearer <token>`.

---

## Contact

**Bar Pesso** — [bar@logigroup.co](mailto:bar@logigroup.co)
