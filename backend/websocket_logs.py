# websocket_logs.py - WebSocket for realtime logs
from fastapi import WebSocket, WebSocketDisconnect
import docker
from docker.errors import NotFound, APIError
from jose import JWTError, jwt
import os
import logging

SECRET_KEY = os.environ.get("DOCKERWEBUI_SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"

clients = {
    "local": docker.from_env(),
}

async def websocket_endpoint(websocket: WebSocket, node: str, container_id: str):
    """WebSocket endpoint to send realtime logs of a Docker container."""
    await websocket.accept()
    
    # Validate token
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401, reason="Missing authentication token")
        return
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            await websocket.close(code=4401, reason="Invalid token")
            return
    except JWTError as e:
        logging.warning(f"JWT validation error: {e}")
        await websocket.close(code=4401, reason="Invalid token")
        return
    
    # Validate node
    if node not in clients:
        await websocket.close(code=4404, reason="Node not found")
        return
    
    try:
        container = clients[node].containers.get(container_id)
        # Stream logs with proper error handling
        for log in container.logs(stream=True, follow=True, tail=100):
            try:
                await websocket.send_text(log.decode('utf-8', errors='replace'))
            except WebSocketDisconnect:
                logging.info(f"Client disconnected from container {container_id} logs")
                break
    except NotFound:
        await websocket.send_text(f"Error: Container {container_id} not found")
        await websocket.close()
    except APIError as e:
        await websocket.send_text(f"Error: Docker API error - {str(e)}")
        await websocket.close()
    except Exception as e:
        logging.error(f"Unexpected error in websocket_endpoint: {e}")
        await websocket.send_text(f"Error: {str(e)}")
        await websocket.close()
