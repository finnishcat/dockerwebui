"""
Comprehensive Docker API tests for DockerWebUI backend.
"""
from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)

def get_valid_token():
    """Helper function to get a valid JWT token."""
    response = client.post("/auth/login", data={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    return response.json()["access_token"]

def test_list_nodes():
    """Test listing available Docker nodes."""
    response = client.get("/docker/nodes")
    assert response.status_code == 200
    nodes = response.json()
    assert isinstance(nodes, list)
    assert "local" in nodes

def test_list_containers_requires_auth():
    """Test that listing containers requires authentication."""
    response = client.get("/docker/containers/local")
    assert response.status_code == 401

def test_list_containers_with_auth():
    """Test listing containers with authentication."""
    token = get_valid_token()
    response = client.get("/docker/containers/local", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_list_containers_invalid_node():
    """Test listing containers with invalid node name."""
    token = get_valid_token()
    response = client.get("/docker/containers/invalid_node", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in [400, 404]

def test_list_images_requires_auth():
    """Test that listing images requires authentication."""
    response = client.get("/docker/images/local")
    assert response.status_code == 401

def test_list_images_with_auth():
    """Test listing images with authentication."""
    token = get_valid_token()
    response = client.get("/docker/images/local", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_list_images_invalid_node():
    """Test listing images with invalid node name."""
    token = get_valid_token()
    response = client.get("/docker/images/invalid_node", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in [400, 404]

def test_stats_requires_auth():
    """Test that getting container stats requires authentication."""
    token = get_valid_token()
    containers = client.get("/docker/containers/local", headers={"Authorization": f"Bearer {token}"}).json()
    if containers:
        container_id = containers[0]["id"]
        response = client.get(f"/docker/stats/local/{container_id}")
        assert response.status_code == 401

def test_stats_with_auth():
    """Test getting container stats with authentication."""
    token = get_valid_token()
    containers = client.get("/docker/containers/local", headers={"Authorization": f"Bearer {token}"}).json()
    if containers:
        container_id = containers[0]["id"]
        response = client.get(f"/docker/stats/local/{container_id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        stats = response.json()
        assert "cpu" in stats
        assert "memory_usage" in stats
        assert "memory_limit" in stats

def test_stats_invalid_container():
    """Test getting stats for non-existent container."""
    token = get_valid_token()
    response = client.get("/docker/stats/local/nonexistentcontainer123", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in [400, 404]

def test_restart_container_requires_auth():
    """Test that restarting a container requires authentication."""
    token = get_valid_token()
    containers = client.get("/docker/containers/local", headers={"Authorization": f"Bearer {token}"}).json()
    if containers:
        container_id = containers[0]["id"]
        response = client.post(f"/docker/container/restart/local/{container_id}")
        assert response.status_code == 401

def test_restart_container_invalid_id():
    """Test restarting a non-existent container."""
    token = get_valid_token()
    response = client.post("/docker/container/restart/local/invalidid", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in [400, 404]

def test_stop_container_requires_auth():
    """Test that stopping a container requires authentication."""
    token = get_valid_token()
    containers = client.get("/docker/containers/local", headers={"Authorization": f"Bearer {token}"}).json()
    if containers:
        container_id = containers[0]["id"]
        response = client.post(f"/docker/container/stop/local/{container_id}")
        assert response.status_code == 401

def test_remove_container_requires_auth():
    """Test that removing a container requires authentication."""
    response = client.post("/docker/container/remove/local/somecontainerid")
    assert response.status_code == 401

def test_pull_image_requires_auth():
    """Test that pulling an image requires authentication."""
    response = client.post("/docker/image/pull/local", json={"image": "alpine:latest"})
    assert response.status_code == 401

def test_pull_image_invalid_format():
    """Test pulling an image with invalid format."""
    token = get_valid_token()
    response = client.post("/docker/image/pull/local", 
                          json={"image": "invalid image name!!"}, 
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422  # Validation error

def test_remove_image_requires_auth():
    """Test that removing an image requires authentication."""
    response = client.delete("/docker/image/remove/local/alpine:latest")
    assert response.status_code == 401

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
