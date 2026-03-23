import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional
from jose import jwt
import bcrypt
from config import USERS_FILE
from storage import load_json, save_json
from auth import get_current_user

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 8

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    avatar: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class CreateUser(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = ""
    email: Optional[str] = ""
    role: Optional[str] = "צופה"


def _get_user(username):
    users = load_json(USERS_FILE, [])
    return next((u for u in users if u["username"] == username), None)


@router.post("/api/auth/login")
def login(req: LoginRequest):
    user = _get_user(req.username)
    if not user:
        raise HTTPException(status_code=401, detail="שם משתמש או סיסמה שגויים")

    if not bcrypt.checkpw(req.password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        raise HTTPException(status_code=401, detail="שם משתמש או סיסמה שגויים")

    payload = {
        "sub": req.username,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/api/auth/profile")
def get_profile(username: str = Depends(get_current_user)):
    user = _get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="משתמש לא נמצא")
    return {
        "username": user["username"],
        "full_name": user.get("full_name", ""),
        "email": user.get("email", ""),
        "role": user.get("role", "מנהל"),
        "avatar": user.get("avatar", ""),
    }


@router.put("/api/auth/profile")
def update_profile(data: ProfileUpdate, username: str = Depends(get_current_user)):
    users = load_json(USERS_FILE, [])
    user = next((u for u in users if u["username"] == username), None)
    if not user:
        raise HTTPException(status_code=404, detail="משתמש לא נמצא")

    if data.full_name is not None:
        user["full_name"] = data.full_name
    if data.email is not None:
        user["email"] = data.email
    if data.role is not None:
        user["role"] = data.role
    if data.avatar is not None:
        user["avatar"] = data.avatar

    save_json(USERS_FILE, users)
    return {"message": "פרטי המשתמש עודכנו"}


@router.put("/api/auth/password")
def change_password(data: PasswordChange, username: str = Depends(get_current_user)):
    users = load_json(USERS_FILE, [])
    user = next((u for u in users if u["username"] == username), None)
    if not user:
        raise HTTPException(status_code=404, detail="משתמש לא נמצא")

    if not bcrypt.checkpw(data.current_password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        raise HTTPException(status_code=400, detail="סיסמה נוכחית שגויה")

    user["password_hash"] = bcrypt.hashpw(data.new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    save_json(USERS_FILE, users)
    return {"message": "הסיסמה שונתה בהצלחה"}


@router.get("/api/auth/users")
def list_users(username: str = Depends(get_current_user)):
    users = load_json(USERS_FILE, [])
    return {"users": [{"username": u["username"], "full_name": u.get("full_name", ""), "email": u.get("email", ""), "role": u.get("role", "מנהל")} for u in users]}


@router.post("/api/auth/users")
def create_user(req: CreateUser, username: str = Depends(get_current_user)):
    users = load_json(USERS_FILE, [])
    if any(u["username"] == req.username for u in users):
        raise HTTPException(status_code=400, detail="שם משתמש כבר קיים")

    password_hash = bcrypt.hashpw(req.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    users.append({
        "username": req.username,
        "password_hash": password_hash,
        "full_name": req.full_name,
        "email": req.email,
        "role": req.role,
    })
    save_json(USERS_FILE, users)
    return {"message": f"משתמש '{req.username}' נוצר בהצלחה"}


@router.delete("/api/auth/users/{target}")
def delete_user(target: str, username: str = Depends(get_current_user)):
    if target == username:
        raise HTTPException(status_code=400, detail="לא ניתן למחוק את עצמך")
    users = load_json(USERS_FILE, [])
    users = [u for u in users if u["username"] != target]
    save_json(USERS_FILE, users)
    return {"message": f"משתמש '{target}' נמחק"}


SETUP_SECRET = os.environ.get("SETUP_SECRET", "")


@router.post("/api/auth/setup")
def setup_user(req: LoginRequest, secret: str = Query("")):
    """One-time user creation. Allowed if: no users exist yet, OR secret matches."""
    users = load_json(USERS_FILE, [])
    no_users_yet = len(users) == 0
    secret_valid = SETUP_SECRET and secret == SETUP_SECRET
    if not no_users_yet and not secret_valid:
        raise HTTPException(status_code=403, detail="אין הרשאה")

    existing = next((u for u in users if u["username"] == req.username), None)
    password_hash = bcrypt.hashpw(req.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    if existing:
        existing["password_hash"] = password_hash
    else:
        users.append({"username": req.username, "password_hash": password_hash, "full_name": "", "email": "", "role": "מנהל"})

    save_json(USERS_FILE, users)
    return {"message": f"User '{req.username}' created"}
