import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from auth import router as auth_router, limiter
from docker_api import router as docker_router
from websocker import websocket_endpoint

logger = logging.getLogger(__name__)

SECRET_KEY = os.environ.get("DOCKERWEBUI_SECRET_KEY", "dev-secret-key")
if SECRET_KEY == "dev-secret-key":
    raise RuntimeError("DOCKERWEBUI_SECRET_KEY is set to default. Set a secure key.")

allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3080")
allow_list = [o.strip() for o in allowed_origins.split(",") if o.strip()]

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")
app.include_router(docker_router, prefix="/docker")
app.add_api_websocket_route("/ws/logs/{node}/{container_id}", websocket_endpoint)
