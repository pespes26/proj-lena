from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from auth import get_current_user, require_admin, ROLES

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
    return {
        "uid": user['uid'],
        "email": user['email'],
        "full_name": user.get("full_name", user['email']),
        "role": user.get("role", "viewer"),
        "linked_manager": user.get("linked_manager", ""),
        "avatar": "",
    }


@router.put("/api/auth/profile")
def update_profile(data: ProfileUpdate, user: dict = Depends(get_current_user)):
    # Phase B: persist profile updates with new data store
    return {"message": "פרטי המשתמש עודכנו"}


# --- Admin only ---

@router.get("/api/auth/users")
def list_users(user: dict = Depends(require_admin)):
    # Phase B: load users from new data store
    raise HTTPException(status_code=503, detail="ניהול משתמשים אינו זמין — נדרש Phase B")


@router.post("/api/auth/users")
def create_user(req: CreateUser, user: dict = Depends(require_admin)):
    # Phase B: create user with new auth provider
    raise HTTPException(status_code=503, detail="יצירת משתמש אינה זמינה — נדרש Phase B")


@router.put("/api/auth/users/{uid}")
def update_user(uid: str, data: UpdateUser, user: dict = Depends(require_admin)):
    # Phase B: update user in new data store
    raise HTTPException(status_code=503, detail="עדכון משתמש אינו זמין — נדרש Phase B")


@router.delete("/api/auth/users/{uid}")
def delete_user(uid: str, user: dict = Depends(require_admin)):
    if uid == user['uid']:
        raise HTTPException(status_code=400, detail="לא ניתן למחוק את עצמך")
    # Phase B: delete user from new auth provider and data store
    raise HTTPException(status_code=503, detail="מחיקת משתמש אינה זמינה — נדרש Phase B")


# --- Setup (first admin) ---

@router.post("/api/auth/setup")
def setup_first_admin(req: CreateUser):
    # Phase B: implement with new auth provider
    raise HTTPException(status_code=503, detail="הגדרת מנהל ראשון אינה זמינה — נדרש Phase B")
