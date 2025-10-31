# docker_api.py - Docker API wrapper
from fastapi import APIRouter, Depends, HTTPException, status
from docker import DockerClient
import docker
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from docker.errors import NotFound, APIError
import os
from typing import List, Optional
import re

router = APIRouter()

# Client Docker disponibili
clients = {
    "local": docker.from_env(),
    # Aggiungi altri nodi se necessario
}

# OAuth2 schema
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Configurazione JWT
SECRET_KEY = os.environ.get("DOCKERWEBUI_SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"

class ImagePullRequest(BaseModel):
    image: str

# Modello utente base
class TokenData(BaseModel):
    username: str

# Verifica e decodifica del token JWT
def get_current_user(token: str = Depends(oauth2_scheme)):
    """Verify and decode the JWT token, returning user data."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenziali non valide",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return TokenData(username=username)
    except JWTError:
        raise credentials_exception

@router.get("/nodes")
def list_nodes():
    """Return the list of available Docker nodes."""
    return list(clients.keys())

class ContainerInfo(BaseModel):
    id: str
    name: str
    image: Optional[list[str]]
    status: str

def validate_node(node: str):
    """Validate the Docker node name (letters, numbers, underscore, max 32 chars)."""
    if not re.match(r"^[a-zA-Z0-9_]{1,32}$", node):
        raise HTTPException(status_code=400, detail="Invalid node name")
    if node not in clients:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

@router.get("/containers/{node}", response_model=List[ContainerInfo])
def list_containers(node: str, user=Depends(get_current_user)):
    node = validate_node(node)
    """Return the list of containers for the specified node."""
    if node not in clients:
        raise HTTPException(status_code=404, detail="Node not found")
    try:
        containers = clients[node].containers.list(all=True)
        return [{
            "id": c.id,
            "name": c.name,
            "image": c.image.tags,
            "status": c.status
        } for c in containers]
    except APIError as e:
        raise HTTPException(status_code=500, detail=str(e))

class ImageInfo(BaseModel):
    id: str
    repo_tags: Optional[list[str]]
    size: int

@router.get("/images/{node}", response_model=List[ImageInfo])
def list_images(node: str, user=Depends(get_current_user)):
    """Return the list of Docker images for the specified node."""
    if node not in clients:
        raise HTTPException(status_code=404, detail="Node not found")
    try:
        images = clients[node].images.list()
        return [{
            "id": img.id,
            "repo_tags": img.tags,
            "size": img.attrs.get("Size", 0)
        } for img in images]
    except APIError as e:
        raise HTTPException(status_code=500, detail=str(e))

class ActionResponse(BaseModel):
    status: str

@router.post("/image/pull/{node}", response_model=ActionResponse)
def pull_image(node: str, body: ImagePullRequest, user=Depends(get_current_user)):
    """Pull a new Docker image."""
    if node not in clients:
        raise HTTPException(status_code=404, detail="Node not found")
    try:
        clients[node].images.pull(body.image)
        return {"status": "ok"}
    except APIError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/image/remove/{node}/{image_id}", response_model=ActionResponse)
def remove_image(node: str, image_id: str, user=Depends(get_current_user)):
    """Remove a Docker image from the specified node."""
    if node not in clients:
        raise HTTPException(status_code=404, detail="Node not found")
    try:
        clients[node].images.remove(image=image_id, force=True)
        return {"status": "ok"}
    except NotFound:
        raise HTTPException(status_code=404, detail="Image not found")
    except APIError as e:
        raise HTTPException(status_code=500, detail=str(e))

class StatsResponse(BaseModel):
    cpu: float
    memory_usage: float
    memory_limit: float
    network_rx: str
    network_tx: str

@router.get("/stats/{node}/{container_id}", response_model=StatsResponse)
def container_stats(node: str, container_id: str, user=Depends(get_current_user)):
    """Return usage statistics (CPU, RAM, network) for a container."""
    if node not in clients:
        raise HTTPException(status_code=404, detail="Node not found")
    try:
        container = clients[node].containers.get(container_id)
        stats = container.stats(stream=False)
        cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
        system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
        cpu = (cpu_delta / system_delta) * len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"]) * 100 if system_delta > 0 else 0
        mem_usage = stats["memory_stats"]["usage"] / 1024 / 1024
        mem_limit = stats["memory_stats"]["limit"] / 1024 / 1024
        net_rx = sum(i["rx_bytes"] for i in stats.get("networks", {}).values()) / 1024
        net_tx = sum(i["tx_bytes"] for i in stats.get("networks", {}).values()) / 1024
        return {
            "cpu": cpu,
            "memory_usage": round(mem_usage, 2),
            "memory_limit": round(mem_limit, 2),
            "network_rx": f"{net_rx:.2f} KB",
            "network_tx": f"{net_tx:.2f} KB"
        }
    except NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except APIError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/container/restart/{node}/{container_id}", response_model=ActionResponse)
def restart_container(node: str, container_id: str, user=Depends(get_current_user)):
    """Restart a Docker container."""
    if node not in clients:
        raise HTTPException(status_code=404, detail="Node not found")
    try:
        container = clients[node].containers.get(container_id)
        container.restart()
        return {"status": "ok"}
    except NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except APIError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/container/stop/{node}/{container_id}", response_model=ActionResponse)
def stop_container(node: str, container_id: str, user=Depends(get_current_user)):
    """Stop a Docker container."""
    if node not in clients:
        raise HTTPException(status_code=404, detail="Node not found")
    try:
        container = clients[node].containers.get(container_id)
        container.stop()
        return {"status": "ok"}
    except NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except APIError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/container/remove/{node}/{container_id}", response_model=ActionResponse)
def remove_container(node: str, container_id: str, user=Depends(get_current_user)):
    """Remove a Docker container."""
    if node not in clients:
        raise HTTPException(status_code=404, detail="Node not found")
    try:
        container = clients[node].containers.get(container_id)
        container.remove(force=True)
        return {"status": "ok"}
    except NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except APIError as e:
        raise HTTPException(status_code=500, detail=str(e))
