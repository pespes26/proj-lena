from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from auth import get_current_user, require_admin, ROLES

router = APIRouter()


# Phase 0.5: firebase_admin and the Firestore-backed user store are gone.
# Profile read still works (data comes from the auth dependency).
# User CRUD + first-admin setup return 503 until Phase D wires Entra
# External ID + Microsoft Graph (or a PostgreSQL users table — TBD).


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


_MIGRATION_DETAIL = "User management migrating to Entra ID — available in Phase D"


# --- Authenticated ---

@router.get("/api/auth/profile")
def get_profile(user: dict = Depends(get_current_user)):
    return {
        "uid": user["uid"],
        "email": user["email"],
        "full_name": user.get("full_name", user["email"]),
        "role": user.get("role", "viewer"),
        "linked_manager": user.get("linked_manager", ""),
        "avatar": "",
    }


# TODO Phase D
@router.put("/api/auth/profile")
def update_profile(data: ProfileUpdate, user: dict = Depends(get_current_user)):
    raise HTTPException(status_code=503, detail=_MIGRATION_DETAIL)


# --- Admin only ---

# TODO Phase D
@router.get("/api/auth/users")
def list_users(user: dict = Depends(require_admin)):
    raise HTTPException(status_code=503, detail=_MIGRATION_DETAIL)


# TODO Phase D
@router.post("/api/auth/users")
def create_user(req: CreateUser, user: dict = Depends(require_admin)):
    raise HTTPException(status_code=503, detail=_MIGRATION_DETAIL)


# TODO Phase D
@router.put("/api/auth/users/{uid}")
def update_user(uid: str, data: UpdateUser, user: dict = Depends(require_admin)):
    raise HTTPException(status_code=503, detail=_MIGRATION_DETAIL)


# TODO Phase D
@router.delete("/api/auth/users/{uid}")
def delete_user(uid: str, user: dict = Depends(require_admin)):
    raise HTTPException(status_code=503, detail=_MIGRATION_DETAIL)


# --- Setup (first admin) ---

# TODO Phase D
@router.post("/api/auth/setup")
def setup_first_admin(req: CreateUser):
    raise HTTPException(status_code=503, detail=_MIGRATION_DETAIL)
