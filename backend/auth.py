import os
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth, firestore
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

# Initialize Firebase Admin SDK
_cred_path = os.path.join(os.path.dirname(__file__), 'firebase-service-account.json')
if os.path.exists(_cred_path):
    cred = credentials.Certificate(_cred_path)
    firebase_admin.initialize_app(cred)
elif os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
    firebase_admin.initialize_app()
else:
    # Default credentials (Cloud Run auto-provides)
    firebase_admin.initialize_app()

db = firestore.client()

ROLES = {
    'admin': 'מנהל מערכת',
    'economist': 'כלכלנית',
    'viewer': 'צופה מלא',
    'project_manager': 'מנהל פרויקט',
}


async def get_current_user(authorization: str = Header(None)) -> dict:
    """Verify Firebase ID token and return user with role from Firestore."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="לא מחובר")
    token = authorization.split(" ", 1)[1]

    # DEV MODE bypass — local development only
    if DEV_MODE and token == DEV_TOKEN:
        return {
            'uid': 'dev-admin',
            'email': 'dev@local',
            'username': 'dev@local',
            'role': 'admin',
            'linked_manager': '',
            'full_name': 'Dev Admin',
        }

    try:
        decoded = firebase_auth.verify_id_token(token, clock_skew_seconds=30)
    except Exception as e:
        print(f"[AUTH ERROR] Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="טוקן לא תקין או פג תוקף")

    uid = decoded.get('uid')
    email = decoded.get('email', '')

    # Get role from Firestore
    doc = db.collection('users').document(uid).get()
    if doc.exists:
        user_data = doc.to_dict()
        role = user_data.get('role', 'viewer')
        linked_manager = user_data.get('linked_manager', '')
        full_name = user_data.get('full_name', '')
    else:
        # First-time login — no Firestore doc yet. Default to viewer.
        role = 'viewer'
        linked_manager = ''
        full_name = email

    return {
        'uid': uid,
        'email': email,
        'username': email,
        'role': role,
        'linked_manager': linked_manager,
        'full_name': full_name,
    }


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
