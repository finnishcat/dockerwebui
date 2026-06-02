from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
import json
import logging
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address

SECRET_KEY = os.environ.get("DOCKERWEBUI_SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

limiter = Limiter(key_func=get_remote_address)

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")


def ensure_users_file():
    if not os.path.exists(USERS_FILE):
        default_password = pwd_context.hash("admin")
        with open(USERS_FILE, "w") as f:
            json.dump([{
                "username": "admin",
                "password": default_password,
                "role": "admin"
            }], f, indent=2)
        logging.warning("Created default users.json (dev only)")

ensure_users_file()

with open(USERS_FILE) as f:
    users_db = json.load(f)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user(username: str):
    return next((user for user in users_db if user["username"] == username), None)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if user and verify_password(password, user["password"]):
        return user
    return None


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


class RegisterRequest(BaseModel):
    username: str
    password: str


@router.post("/register")
@limiter.limit("5/hour")
def register(request: Request, body: RegisterRequest):
    if len(users_db) > 0:
        raise HTTPException(status_code=403, detail="Registration not allowed: a user already exists")
    if len(body.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    hashed = pwd_context.hash(body.password)
    user = {"username": body.username, "password": hashed, "role": "admin"}
    users_db.append(user)
    with open(USERS_FILE, "w") as f:
        json.dump(users_db, f, indent=2)
    return {"msg": "Admin user created"}


@router.post("/login")
@limiter.limit("10/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer"}
