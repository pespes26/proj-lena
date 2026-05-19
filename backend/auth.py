import os
from fastapi import Header, HTTPException, Depends

# Load .env if present (local dev)
_env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and '=' in _line and not _line.startswith('#'):
                _k, _v = _line.split('=', 1)
                os.environ.setdefault(_k.strip(), _v.strip())

DEV_MODE = os.environ.get('DEV_MODE', '').lower() in ('true', '1')
DEV_TOKEN = 'dev-admin-local'


# Phase 0: Firebase has been ripped out. Entra External ID JWT verification
# lands in Phase C; the Firestore-backed user store moves to PostgreSQL in
# Phase B. Until then, anything that touches `db` or tries to verify a real
# token hits one of these stubs and fails loudly. DEV_MODE remains the only
# way through.

class _FirestoreStub:
    """Placeholder that errors loudly if anyone tries to talk to Firestore."""

    def __getattr__(self, name):
        raise RuntimeError(
            "Firestore has been removed (Phase 0). "
            "Use storage.py JSON helpers until Phase B PostgreSQL lands."
        )

    def collection(self, *_args, **_kwargs):
        raise RuntimeError(
            "Firestore has been removed (Phase 0). "
            "Use storage.py JSON helpers until Phase B PostgreSQL lands."
        )

    def batch(self, *_args, **_kwargs):
        raise RuntimeError(
            "Firestore has been removed (Phase 0). "
            "Use storage.py JSON helpers until Phase B PostgreSQL lands."
        )


db = _FirestoreStub()


ROLES = {
    'admin': 'מנהל מערכת',
    'economist': 'כלכלנית',
    'viewer': 'צופה מלא',
    'project_manager': 'מנהל פרויקט',
}


async def get_current_user(authorization: str = Header(None)) -> dict:
    """Verify token and return user.

    Phase 0: only the DEV_MODE token is accepted. Real JWT verification
    (Entra External ID) lands in Phase C.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="לא מחובר")
    token = authorization.split(" ", 1)[1]

    if DEV_MODE and token == DEV_TOKEN:
        return {
            'uid': 'dev-admin',
            'email': 'dev@local',
            'username': 'dev@local',
            'role': 'admin',
            'linked_manager': '',
            'full_name': 'Dev Admin',
        }

    raise HTTPException(
        status_code=503,
        detail="Authentication backend is being migrated. Enable DEV_MODE until Phase C.",
    )


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="נדרשת הרשאת מנהל מערכת")
    return user


async def require_editor(user: dict = Depends(get_current_user)) -> dict:
    if user['role'] not in ('admin', 'economist'):
        raise HTTPException(status_code=403, detail="נדרשת הרשאת עריכה")
    return user


def check_project_owner(project_name: str, user: dict):
    """Check if user owns the project (for project_manager limited edit)."""
    if user['role'] in ('admin', 'economist'):
        return True
    if user['role'] == 'project_manager':
        from services.unified import load_form_data
        form_data = load_form_data()
        project = form_data.get(project_name, {})
        return project.get('manager', '') == user.get('linked_manager', '')
    return False
