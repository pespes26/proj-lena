from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from firebase_admin import auth as firebase_auth
from auth import get_current_user, require_admin, db, ROLES

router = APIRouter()


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar: Optional[str] = None


class CreateUser(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = ""
    role: Optional[str] = "viewer"
    linked_manager: Optional[str] = ""


class UpdateUser(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    linked_manager: Optional[str] = None


# --- Authenticated ---

@router.get("/api/auth/profile")
def get_profile(user: dict = Depends(get_current_user)):
    try:
        doc = db.collection('users').document(user['uid']).get()
        data = doc.to_dict() if doc.exists else {}
    except Exception:
        data = {}
    return {
        "uid": user['uid'],
        "email": user['email'],
        "full_name": data.get("full_name", user.get("full_name", user['email'])),
        "role": data.get("role", user.get("role", "viewer")),
        "linked_manager": data.get("linked_manager", user.get("linked_manager", "")),
        "avatar": data.get("avatar", ""),
    }


@router.put("/api/auth/profile")
def update_profile(data: ProfileUpdate, user: dict = Depends(get_current_user)):
    updates = {}
    if data.full_name is not None:
        updates["full_name"] = data.full_name
    if data.avatar is not None:
        updates["avatar"] = data.avatar
    if updates:
        db.collection('users').document(user['uid']).set(updates, merge=True)
    return {"message": "פרטי המשתמש עודכנו"}


# --- Admin only ---

@router.get("/api/auth/users")
def list_users(user: dict = Depends(require_admin)):
    docs = db.collection('users').stream()
    users = []
    for doc in docs:
        d = doc.to_dict()
        users.append({
            "uid": doc.id,
            "email": d.get("email", ""),
            "full_name": d.get("full_name", ""),
            "role": d.get("role", "viewer"),
            "linked_manager": d.get("linked_manager", ""),
        })
    return {"users": users}


@router.post("/api/auth/users")
def create_user(req: CreateUser, user: dict = Depends(require_admin)):
    try:
        # Create Firebase Auth user
        fb_user = firebase_auth.create_user(
            email=req.email,
            password=req.password,
            display_name=req.full_name or req.email,
        )
    except firebase_auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=400, detail="כתובת אימייל כבר קיימת")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה ביצירת משתמש: {str(e)}")

    # Create Firestore doc with role
    db.collection('users').document(fb_user.uid).set({
        "email": req.email,
        "full_name": req.full_name or "",
        "role": req.role or "viewer",
        "linked_manager": req.linked_manager if req.role == 'project_manager' else '',
        "avatar": "",
    })

    return {"message": f"משתמש '{req.email}' נוצר בהצלחה", "uid": fb_user.uid}


@router.put("/api/auth/users/{uid}")
def update_user(uid: str, data: UpdateUser, user: dict = Depends(require_admin)):
    doc_ref = db.collection('users').document(uid)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="משתמש לא נמצא")

    updates = {}
    if data.full_name is not None:
        updates["full_name"] = data.full_name
    if data.role is not None:
        updates["role"] = data.role
    if data.linked_manager is not None:
        updates["linked_manager"] = data.linked_manager

    if updates:
        doc_ref.set(updates, merge=True)
    return {"message": "משתמש עודכן"}


@router.delete("/api/auth/users/{uid}")
def delete_user(uid: str, user: dict = Depends(require_admin)):
    if uid == user['uid']:
        raise HTTPException(status_code=400, detail="לא ניתן למחוק את עצמך")

    # Delete from Firebase Auth
    try:
        firebase_auth.delete_user(uid)
    except Exception:
        pass  # May not exist in Auth

    # Delete from Firestore
    db.collection('users').document(uid).delete()
    return {"message": "משתמש נמחק"}


# --- Setup (first admin) ---

@router.post("/api/auth/setup")
def setup_first_admin(req: CreateUser):
    """Create first admin user. Only works if no users exist in Firestore."""
    docs = list(db.collection('users').limit(1).stream())
    if len(docs) > 0:
        raise HTTPException(status_code=403, detail="כבר קיימים משתמשים. צור משתמשים דרך ניהול.")

    try:
        fb_user = firebase_auth.create_user(
            email=req.email,
            password=req.password,
            display_name=req.full_name or req.email,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"שגיאה ביצירת משתמש: {str(e)}")

    db.collection('users').document(fb_user.uid).set({
        "email": req.email,
        "full_name": req.full_name or "",
        "role": "admin",
        "linked_manager": "",
        "avatar": "",
    })

    return {"message": f"Admin '{req.email}' created", "uid": fb_user.uid}
