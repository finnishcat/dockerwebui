# auth.py - JWT Authentication
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
import json
import logging
from pydantic import BaseModel

SECRET_KEY = os.environ.get("DOCKERWEBUI_SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()
# Use bcrypt_sha256 to avoid bcrypt 72-byte limitation and preserve entropy for long inputs
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

def hash_password(password: str) -> str:
    """Hash password using configured pwd_context (bcrypt_sha256)."""
    return pwd_context.hash(password)


def ensure_users_file():
    """Create a default users.json file with admin user if it does not exist (development only)."""
    if not os.path.exists(USERS_FILE):
        # Create with a safe hash function that handles long inputs
        default_password = hash_password("admin")
        with open(USERS_FILE, "w") as f:
            json.dump([{
                "username": "admin",
                "password": default_password,
                "role": "admin"
            }], f, indent=2)
        logging.warning("Created default users.json with admin user (development only). Change the password in production!")

# NOTE: ensure_users_file() is intentionally NOT called at import time to avoid import-side effects
# Call ensure_users_file() during application startup so tests that import modules do not trigger hashing.

# Initialize users_db as an empty list to avoid import-time file reads
users_db = []

def load_users_db():
    """Load the users database from the users.json file."""
    global users_db
    with open(USERS_FILE) as f:
        users_db = json.load(f)

def verify_password(plain_password, hashed_password):
    """Verify that the provided password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    """Return the user from the user database given the username."""
    return next((user for user in users_db if user["username"] == username), None)

def authenticate_user(username: str, password: str):
    """Authenticate a user by verifying username and password."""
    user = get_user(username)
    if user and verify_password(password, user["password"]):
        return user
    return None

def create_access_token(data: dict):
    """Create a JWT token with the provided data."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

class RegisterRequest(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(request: RegisterRequest):
    """Allow creation of the first admin user if no users exist."""
    if len(users_db) > 0:
        raise HTTPException(status_code=403, detail="Registration not allowed: a user already exists.")
    hashed = hash_password(request.password)
    user = {"username": request.username, "password": hashed, "role": "admin"}
    users_db.append(user)
    with open(USERS_FILE, "w") as f:
        json.dump(users_db, f, indent=2)
    return {"msg": "Admin user created"}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint for user authentication and JWT generation."""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer"}