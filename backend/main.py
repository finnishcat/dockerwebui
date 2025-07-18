# main.py - FastAPI backend entry point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from docker_api import router as docker_router
from websocker import websocket_endpoint

app = FastAPI()

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routing
app.include_router(auth_router, prefix="/auth")
app.include_router(docker_router, prefix="/docker")

# WebSocket logs realtime
app.add_api_websocket_route("/ws/logs/{node}/{container_id}", websocket_endpoint)
