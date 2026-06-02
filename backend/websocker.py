"""WebSocket endpoint to stream container logs without blocking the event loop."""
import os
import logging
import threading
import asyncio
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect
import docker
from jose import JWTError, jwt

logger = logging.getLogger(__name__)

SECRET_KEY = os.environ.get("DOCKERWEBUI_SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"

clients = {
    "local": docker.from_env(),
}


async def websocket_endpoint(websocket: WebSocket, node: str, container_id: str):
    """WebSocket endpoint to send realtime logs of a Docker container.

    This implementation streams logs from the blocking Docker SDK in a separate
    thread and schedules sends on the asyncio loop using
    asyncio.run_coroutine_threadsafe().
    """
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

    if node not in clients:
        await websocket.send_text("Error: Node not found")
        await websocket.close()
        return

    try:
        container = clients[node].containers.get(container_id)
    except Exception:
        await websocket.send_text("Error: Container not found")
        await websocket.close()
        return

    loop = asyncio.get_event_loop()

    def stream_logs():
        try:
            for raw in container.logs(stream=True, follow=True):
                if raw is None:
                    continue
                text = raw.decode(errors="replace")
                try:
                    fut = asyncio.run_coroutine_threadsafe(websocket.send_text(text), loop)
                    # wait briefly for send result to detect disconnection
                    fut.result(timeout=5)
                except Exception as e:
                    logger.info("WebSocket send failed or client disconnected: %s", e)
                    break
        except Exception as e:
            logger.exception("Error while streaming logs: %s", e)
        finally:
            try:
                asyncio.run_coroutine_threadsafe(websocket.close(), loop)
            except Exception:
                pass

    t = threading.Thread(target=stream_logs, daemon=True)
    t.start()

    # Wait until client disconnects. receive_text will raise WebSocketDisconnect on close.
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected for container %s", container_id)
    finally:
        # thread will terminate when send fails; ensure join with timeout
        try:
            t.join(timeout=1)
        except Exception:
            pass
