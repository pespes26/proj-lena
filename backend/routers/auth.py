import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from jose import jwt
import bcrypt
from config import USERS_FILE
from storage import load_json, save_json

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 8

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/api/auth/login")
def login(req: LoginRequest):
    users = load_json(USERS_FILE, [])
    user = next((u for u in users if u["username"] == req.username), None)
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


SETUP_SECRET = os.environ.get("SETUP_SECRET", "")


@router.post("/api/auth/setup")
def setup_user(req: LoginRequest, secret: str = Query("")):
    """One-time user creation endpoint. Requires SETUP_SECRET env var."""
    if not SETUP_SECRET or secret != SETUP_SECRET:
        raise HTTPException(status_code=403, detail="אין הרשאה")

    users = load_json(USERS_FILE, [])
    existing = next((u for u in users if u["username"] == req.username), None)
    password_hash = bcrypt.hashpw(req.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    if existing:
        existing["password_hash"] = password_hash
    else:
        users.append({"username": req.username, "password_hash": password_hash})

    save_json(USERS_FILE, users)
    return {"message": f"User '{req.username}' created"}
