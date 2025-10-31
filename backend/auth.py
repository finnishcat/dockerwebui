# auth.py - JWT Authentication
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import os
import json
import logging
import re
from pydantic import BaseModel, Field, field_validator

# Validate SECRET_KEY is set properly in production
SECRET_KEY = os.environ.get("DOCKERWEBUI_SECRET_KEY", "dev-secret-key")
if SECRET_KEY == "dev-secret-key":
    logging.warning("⚠️  Using default SECRET_KEY! Set DOCKERWEBUI_SECRET_KEY environment variable in production!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash della password, troncata a 72 byte (limite bcrypt)."""
    pw_bytes = password.encode('utf-8')
    if len(pw_bytes) > 72:
        pw_bytes = pw_bytes[:72]
        password = pw_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

def hash_password(password: str) -> str:
    """Hash password using configured pwd_context (bcrypt_sha256)."""
    return pwd_context.hash(password)


def ensure_users_file():
    """Create a default users.json file with admin user if it does not exist (development only)."""
    if not os.path.exists(USERS_FILE):
        default_password = hash_password("admin")
        with open(USERS_FILE, "w") as f:
            json.dump([{
                "username": "admin",
                "password": default_password,
                "role": "admin"
            }], f, indent=2)
        logging.warning("⚠️  Created default users.json with admin/admin credentials. Change immediately in production!")

# NOTE: ensure_users_file() is intentionally NOT called at import time to avoid import-side effects
# Call ensure_users_file() during application startup so tests that import modules do not trigger hashing.

# Initialize users_db as an empty list to avoid import-time file reads
users_db = []

def load_users():
    """Load users from file."""
    try:
        with open(USERS_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logging.error(f"Error loading users file: {e}")
        return []

users_db = load_users()

def save_users():
    """Save users to file."""
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users_db, f, indent=2)
    except IOError as e:
        logging.error(f"Error saving users file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save user data")

def verify_password(plain_password, hashed_password):
    """Verify that the provided password matches the stored hash."""
    return pwd_context.verify(plain_password[:72], hashed_password)

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
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=32, description="Username (3-32 characters)")
    password: str = Field(..., min_length=8, max_length=128, description="Password (min 8 characters)")
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username must contain only letters, numbers, underscore, and hyphen')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

@router.post("/register")
def register(request: RegisterRequest):
    """Allow creation of the first admin user if no users exist."""
    if len(users_db) > 0:
        raise HTTPException(status_code=403, detail="Registration not allowed: a user already exists.")
    
    # Check if username already exists (shouldn't happen but double check)
    if get_user(request.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed = hash_password(request.password)
    user = {"username": request.username, "password": hashed, "role": "admin"}
    users_db.append(user)
    save_users()
    return {"msg": "Admin user created"}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint for user authentication and JWT generation."""
    # Basic input validation
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username and password are required"
        )
    
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer"}