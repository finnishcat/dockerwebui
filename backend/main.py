# main.py - FastAPI backend entry point
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from auth import router as auth_router
from docker_api import router as docker_router
from websocket_logs import websocket_endpoint

app = FastAPI(
    title="DockerWebUI API",
    description="API for managing Docker containers",
    version="1.0.0"
)

# Get allowed origins from environment or use defaults
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3080").split(",")

# CORS for React frontend - more restrictive in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],  # Only needed methods
    allow_headers=["Authorization", "Content-Type"],
)

# Security: Add trusted host middleware to prevent host header attacks
# In production, set TRUSTED_HOSTS environment variable
trusted_hosts = os.environ.get("TRUSTED_HOSTS", "*").split(",")
if trusted_hosts != ["*"]:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

# API Routing
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(docker_router, prefix="/docker", tags=["Docker"])

# WebSocket logs realtime
app.add_api_websocket_route("/ws/logs/{node}/{container_id}", websocket_endpoint)

@app.get("/", tags=["Health"])
def read_root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "DockerWebUI API"}
