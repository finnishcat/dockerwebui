from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from docker.errors import NotFound, APIError
import docker
import os
import json
import re
import io
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

SECRET_KEY = os.environ.get("DOCKERWEBUI_SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

ALLOWED_IMAGE_PATTERN = re.compile(r'^[a-zA-Z0-9._\-/:]+$')
ALLOWED_ID_PATTERN = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_.\-:]*$')

DEFAULT_NODES = {"local": "unix:///var/run/docker.sock"}
raw_nodes = os.environ.get("DOCKERWEBUI_NODES", "")
clients = {}
try:
    if raw_nodes:
        parsed = json.loads(raw_nodes)
        for name, url in parsed.items():
            clients[name] = docker.DockerClient(base_url=url)
    else:
        clients["local"] = docker.from_env()
except Exception as e:
    logger.warning("Failed to initialize custom nodes, falling back to local: %s", e)
    clients["local"] = docker.from_env()


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing subject")
        return {"username": username, "role": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def sanitize_id(value: str) -> str:
    if not ALLOWED_ID_PATTERN.match(value):
        raise HTTPException(status_code=400, detail=f"Invalid identifier: {value}")
    return value


def sanitize_image_name(value: str) -> str:
    if not ALLOWED_IMAGE_PATTERN.match(value):
        raise HTTPException(status_code=400, detail=f"Invalid image name: {value}")
    return value


def get_client(node: str):
    if node not in clients:
        raise HTTPException(status_code=404, detail=f"Node '{node}' not found")
    return clients[node]


@router.get("/containers/{node}")
def list_containers(node: str, all: bool = True, user=Depends(verify_token)):
    sanitize_id(node)
    client = get_client(node)
    try:
        containers = client.containers.list(all=all)
        result = []
        for c in containers:
            result.append({
                "id": c.id,
                "name": c.name,
                "image": c.image.tags if c.image else [],
                "status": c.status,
                "created": c.attrs.get("Created", ""),
                "ports": c.attrs.get("NetworkSettings", {}).get("Ports", {}),
            })
        return result
    except APIError as e:
        raise HTTPException(status_code=502, detail="Docker API error")
    except Exception as e:
        logger.exception("Error listing containers")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/images/{node}")
def list_images(node: str, user=Depends(verify_token)):
    sanitize_id(node)
    client = get_client(node)
    try:
        images = client.images.list(all=False)
        result = []
        for img in images:
            result.append({
                "id": img.id,
                "repo_tags": img.tags or [],
                "size": img.attrs.get("Size", 0),
                "created": img.attrs.get("Created", ""),
            })
        return result
    except APIError:
        raise HTTPException(status_code=502, detail="Docker API error")
    except Exception as e:
        logger.exception("Error listing images")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats/{node}/{container_id}")
def container_stats(node: str, container_id: str, user=Depends(verify_token)):
    sanitize_id(node)
    sanitize_id(container_id)
    client = get_client(node)
    try:
        container = client.containers.get(container_id)
        stats = container.stats(stream=False)
        cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
        system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
        num_cpus = stats["cpu_stats"]["online_cpus"] or 1
        cpu_percent = 0.0
        if system_delta > 0 and cpu_delta > 0:
            cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0
        mem_stats = stats.get("memory_stats", {})
        mem_usage = mem_stats.get("usage", 0)
        mem_limit = mem_stats.get("limit", 1)
        mem_usage_mb = round(mem_usage / (1024 * 1024), 2)
        mem_limit_mb = round(mem_limit / (1024 * 1024), 2)
        net_stats = stats.get("networks", {})
        rx = sum(n.get("rx_bytes", 0) for n in net_stats.values())
        tx = sum(n.get("tx_bytes", 0) for n in net_stats.values())
        return {
            "cpu": round(cpu_percent, 2),
            "memory_usage": mem_usage_mb,
            "memory_limit": mem_limit_mb,
            "network_rx": rx,
            "network_tx": tx,
        }
    except NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except APIError:
        raise HTTPException(status_code=502, detail="Docker API error")
    except Exception as e:
        logger.exception("Error fetching stats")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/container/restart/{node}/{container_id}")
def restart_container(node: str, container_id: str, user=Depends(verify_token)):
    sanitize_id(node)
    sanitize_id(container_id)
    client = get_client(node)
    try:
        container = client.containers.get(container_id)
        container.restart()
        return {"msg": f"Container {container_id} restarted"}
    except NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except APIError:
        raise HTTPException(status_code=502, detail="Docker API error")
    except Exception as e:
        logger.exception("Error restarting container")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/container/stop/{node}/{container_id}")
def stop_container(node: str, container_id: str, user=Depends(verify_token)):
    sanitize_id(node)
    sanitize_id(container_id)
    client = get_client(node)
    try:
        container = client.containers.get(container_id)
        container.stop()
        return {"msg": f"Container {container_id} stopped"}
    except NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except APIError:
        raise HTTPException(status_code=502, detail="Docker API error")
    except Exception as e:
        logger.exception("Error stopping container")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/container/remove/{node}/{container_id}")
def remove_container(node: str, container_id: str, force: bool = True, user=Depends(verify_token)):
    sanitize_id(node)
    sanitize_id(container_id)
    client = get_client(node)
    try:
        container = client.containers.get(container_id)
        container.remove(force=force)
        return {"msg": f"Container {container_id} removed"}
    except NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except APIError:
        raise HTTPException(status_code=502, detail="Docker API error")
    except Exception as e:
        logger.exception("Error removing container")
        raise HTTPException(status_code=500, detail="Internal server error")


class PullRequest(BaseModel):
    image: str


@router.post("/image/pull/{node}")
def pull_image(node: str, req: PullRequest, user=Depends(verify_token)):
    sanitize_id(node)
    image_name = sanitize_image_name(req.image)
    client = get_client(node)
    try:
        for line in client.images.pull(image_name, stream=True, decode=True):
            if "error" in line:
                raise HTTPException(status_code=400, detail=line["error"])
        return {"msg": f"Image {image_name} pulled successfully"}
    except HTTPException:
        raise
    except APIError as e:
        raise HTTPException(status_code=502, detail=f"Docker API error: {e}")
    except Exception as e:
        logger.exception("Error pulling image")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/image/remove/{node}/{image_id}")
def remove_image(node: str, image_id: str, force: bool = False, user=Depends(verify_token)):
    sanitize_id(node)
    sanitize_id(image_id)
    client = get_client(node)
    try:
        client.images.remove(image_id, force=force)
        return {"msg": f"Image {image_id} removed"}
    except NotFound:
        raise HTTPException(status_code=404, detail="Image not found")
    except APIError:
        raise HTTPException(status_code=502, detail="Docker API error")
    except Exception as e:
        logger.exception("Error removing image")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/image/save/{node}/{image_id}")
def save_image(node: str, image_id: str, user=Depends(verify_token)):
    sanitize_id(node)
    sanitize_id(image_id)
    if node not in clients:
        raise HTTPException(status_code=404, detail=f"Node '{node}' not found")
    client = get_client(node)
    try:
        api_client = client.api
        chunks = list(api_client.get_image(image_id))
        tar_data = b"".join(chunks)
        safe_name = image_id.replace(":", "_").replace("/", "_").replace("@", "_")
        return StreamingResponse(
            io.BytesIO(tar_data),
            media_type="application/x-tar",
            headers={
                "Content-Disposition": f'attachment; filename="{safe_name}.tar"',
            }
        )
    except NotFound:
        raise HTTPException(status_code=404, detail="Image not found")
    except APIError:
        raise HTTPException(status_code=502, detail="Docker API error")
    except Exception as e:
        logger.exception("Error saving image")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/image/load/{node}")
async def load_image(node: str, file: UploadFile = File(...), user=Depends(verify_token)):
    sanitize_id(node)
    if node not in clients:
        raise HTTPException(status_code=404, detail=f"Node '{node}' not found")
    client = get_client(node)
    try:
        content = await file.read()
        api_client = client.api
        result = api_client.load_image(io.BytesIO(content))
        image_ids = []
        for item in result:
            if isinstance(item, dict) and item.get("status"):
                image_ids.append(item["status"])
        loaded = ", ".join(image_ids) if image_ids else "image loaded"
        return {"msg": f"Image loaded: {loaded}"}
    except APIError as e:
        raise HTTPException(status_code=502, detail=f"Docker API error: {e}")
    except Exception as e:
        logger.exception("Error loading image")
        raise HTTPException(status_code=500, detail="Internal server error")
