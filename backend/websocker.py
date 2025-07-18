# websocket_logs.py - WebSocket for realtime logs
from fastapi import WebSocket
import docker
from jose import JWTError, jwt
import os

SECRET_KEY = os.environ.get("DOCKERWEBUI_SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"

clients = {
    "local": docker.from_env(),
}

async def websocket_endpoint(websocket: WebSocket, node: str, container_id: str):
    """WebSocket endpoint to send realtime logs of a Docker container."""
    await websocket.accept()
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401)
        return
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        await websocket.close(code=4401)
        return
    try:
        container = clients[node].containers.get(container_id)
        for log in container.logs(stream=True, follow=True):
            await websocket.send_text(log.decode())
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
        await websocket.close()
