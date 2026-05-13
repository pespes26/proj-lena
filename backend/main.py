import os

# Load .env before any other imports (local dev)
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and '=' in _line and not _line.startswith('#'):
                _k, _v = _line.split('=', 1)
                os.environ.setdefault(_k.strip(), _v.strip())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import projects, cashflow, dashboard, reports, project_form, auth, ai
from middleware import RequestLoggingMiddleware
from exception_handlers import global_exception_handler

ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app = FastAPI(title="IFMLogiX - P&L & Cash Flow")

app.add_exception_handler(Exception, global_exception_handler)

# Starlette applies middleware in reverse-registration order (last added = outermost).
# CORSMiddleware registered first → RequestLoggingMiddleware registered second
# → logging wraps everything, including CORS rejections.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(cashflow.router)
app.include_router(dashboard.router)
app.include_router(reports.router)
app.include_router(project_form.router)
app.include_router(ai.router)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/debug-dev")
def debug_dev():
    import os
    return {"DEV_MODE_env": os.environ.get("DEV_MODE", "NOT_SET"), "env_path_exists": os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))}

# Serve frontend static files in production
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'dist')
if os.path.exists(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the Vue SPA for all non-API routes."""
        file_path = os.path.join(STATIC_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
