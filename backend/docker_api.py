# docker_api.py - Docker API wrapper
from fastapi import APIRouter, Depends, HTTPException, status
from docker import DockerClient
import docker
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field, field_validator
from docker.errors import NotFound, APIError
import os
import logging
from typing import List, Optional
import re

router = APIRouter()

# Docker clients available
clients = {
    "local": docker.from_env(),
    # Add other nodes if needed
}

# OAuth2 schema
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# JWT configuration
SECRET_KEY = os.environ.get("DOCKERWEBUI_SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"

class ImagePullRequest(BaseModel):
    image: str = Field(..., min_length=1, max_length=255, description="Docker image name")
    
    @field_validator('image')
    @classmethod
    def validate_image(cls, v: str) -> str:
        """Validate Docker image name format."""
        # Basic validation for Docker image names
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9._/-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]+$', v):
            raise ValueError('Invalid Docker image name format')
        return v

# Base user model
class TokenData(BaseModel):
    username: str

# Verify and decode JWT token
def get_current_user(token: str = Depends(oauth2_scheme)):
    """Verify and decode the JWT token, returning user data."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return TokenData(username=username)
    except JWTError as e:
        logging.warning(f"JWT decode error: {e}")
        raise credentials_exception
        raise credentials_exception

def validate_node(node: str):
    """Validate the Docker node name (letters, numbers, underscore, max 32 chars)."""
    if not re.match(r"^[a-zA-Z0-9_]{1,32}$", node):
        raise HTTPException(status_code=400, detail="Invalid node name")
    if node not in clients:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

def validate_container_id(container_id: str):
    """Validate container ID format."""
    if not re.match(r"^[a-zA-Z0-9]{12,64}$", container_id):
        raise HTTPException(status_code=400, detail="Invalid container ID format")
    return container_id

def validate_image_id(image_id: str):
    """Validate image ID format."""
    # Allow both short and long image IDs, as well as image names with tags
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9._:/-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]+$", image_id):
        raise HTTPException(status_code=400, detail="Invalid image ID format")
    return image_id

pwd_context = None  # Not needed in this module

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
    """Return the list of containers for the specified node."""
    node = validate_node(node)
    try:
        containers = clients[node].containers.list(all=True)
        return [{
            "id": c.id,
            "name": c.name,
            "image": c.image.tags,
            "status": c.status
        } for c in containers]
    except APIError as e:
        logging.error(f"Docker API error listing containers: {e}")
        raise HTTPException(status_code=500, detail=f"Docker API error: {str(e)}")

class ImageInfo(BaseModel):
    id: str
    repo_tags: Optional[list[str]]
    size: int

@router.get("/images/{node}", response_model=List[ImageInfo])
def list_images(node: str, user=Depends(get_current_user)):
    """Return the list of Docker images for the specified node."""
    node = validate_node(node)
    try:
        images = clients[node].images.list()
        return [{
            "id": img.id,
            "repo_tags": img.tags,
            "size": img.attrs.get("Size", 0)
        } for img in images]
    except APIError as e:
        logging.error(f"Docker API error listing images: {e}")
        raise HTTPException(status_code=500, detail=f"Docker API error: {str(e)}")

class ActionResponse(BaseModel):
    status: str

@router.post("/image/pull/{node}", response_model=ActionResponse)
def pull_image(node: str, body: ImagePullRequest, user=Depends(get_current_user)):
    """Pull a new Docker image."""
    node = validate_node(node)
    try:
        clients[node].images.pull(body.image)
        return {"status": "ok"}
    except APIError as e:
        logging.error(f"Docker API error pulling image: {e}")
        raise HTTPException(status_code=500, detail=f"Docker API error: {str(e)}")

@router.delete("/image/remove/{node}/{image_id}", response_model=ActionResponse)
def remove_image(node: str, image_id: str, user=Depends(get_current_user)):
    """Remove a Docker image from the specified node."""
    node = validate_node(node)
    image_id = validate_image_id(image_id)
    try:
        clients[node].images.remove(image=image_id, force=True)
        return {"status": "ok"}
    except NotFound:
        raise HTTPException(status_code=404, detail="Image not found")
    except APIError as e:
        logging.error(f"Docker API error removing image: {e}")
        raise HTTPException(status_code=500, detail=f"Docker API error: {str(e)}")

class StatsResponse(BaseModel):
    cpu: float
    memory_usage: float
    memory_limit: float
    network_rx: str
    network_tx: str

@router.get("/stats/{node}/{container_id}", response_model=StatsResponse)
def container_stats(node: str, container_id: str, user=Depends(get_current_user)):
    """Return usage statistics (CPU, RAM, network) for a container."""
    node = validate_node(node)
    container_id = validate_container_id(container_id)
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
            "cpu": round(cpu, 2),
            "memory_usage": round(mem_usage, 2),
            "memory_limit": round(mem_limit, 2),
            "network_rx": f"{net_rx:.2f} KB",
            "network_tx": f"{net_tx:.2f} KB"
        }
    except NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except (KeyError, ZeroDivisionError) as e:
        logging.error(f"Error parsing container stats: {e}")
        raise HTTPException(status_code=500, detail="Error parsing container statistics")
    except APIError as e:
        logging.error(f"Docker API error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Docker API error: {str(e)}")

@router.post("/container/restart/{node}/{container_id}", response_model=ActionResponse)
def restart_container(node: str, container_id: str, user=Depends(get_current_user)):
    """Restart a Docker container."""
    node = validate_node(node)
    container_id = validate_container_id(container_id)
    try:
        container = clients[node].containers.get(container_id)
        container.restart()
        return {"status": "ok"}
    except NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except APIError as e:
        logging.error(f"Docker API error restarting container: {e}")
        raise HTTPException(status_code=500, detail=f"Docker API error: {str(e)}")

@router.post("/container/stop/{node}/{container_id}", response_model=ActionResponse)
def stop_container(node: str, container_id: str, user=Depends(get_current_user)):
    """Stop a Docker container."""
    node = validate_node(node)
    container_id = validate_container_id(container_id)
    try:
        container = clients[node].containers.get(container_id)
        container.stop()
        return {"status": "ok"}
    except NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except APIError as e:
        logging.error(f"Docker API error stopping container: {e}")
        raise HTTPException(status_code=500, detail=f"Docker API error: {str(e)}")

@router.post("/container/remove/{node}/{container_id}", response_model=ActionResponse)
def remove_container(node: str, container_id: str, user=Depends(get_current_user)):
    """Remove a Docker container."""
    node = validate_node(node)
    container_id = validate_container_id(container_id)
    try:
        container = clients[node].containers.get(container_id)
        container.remove(force=True)
        return {"status": "ok"}
    except NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except APIError as e:
        logging.error(f"Docker API error removing container: {e}")
        raise HTTPException(status_code=500, detail=f"Docker API error: {str(e)}")
