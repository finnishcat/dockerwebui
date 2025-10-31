import os
os.environ["PASSLIB_BCRYPT_BACKEND"] = "builtin"
from fastapi.testclient import TestClient
from main import app
import pytest

@pytest.fixture(scope="module")
def client():
    """Create TestClient as context manager to trigger startup/shutdown events. Ricrea admin."""
    import os
    users_file = os.path.join(os.path.dirname(__file__), "users.json")
    if os.path.exists(users_file):
        os.remove(users_file)
    from auth import ensure_users_file
    ensure_users_file()
    with TestClient(app) as c:
        yield c

def get_token(client):
    """Get a valid JWT token for the admin user."""
    res = client.post("/auth/login", data={"username": "admin", "password": "admin"})
    assert res.status_code == 200
    return res.json()["access_token"]

def test_login(client):
    """Test login and JWT token generation."""
    res = client.post("/auth/login", data={"username": "admin", "password": "admin"})
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_list_containers(client):
    """Test listing Docker containers."""
    token = get_token(client)
    res = client.get("/docker/containers/local", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_list_images(client):
    """Test listing Docker images."""
    token = get_token(client)
    res = client.get("/docker/images/local", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_stats(client):
    """Test requesting statistics for a container."""
    token = get_token(client)
    # Prendi un container esistente
    containers = client.get("/docker/containers/local", headers={"Authorization": f"Bearer {token}"}).json()
    if containers:
        cid = containers[0]["id"]
        res = client.get(f"/docker/stats/local/{cid}", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        assert "cpu" in res.json()

def test_restart_stop_remove_container(client):
    """Test restart, stop, and remove actions on a Docker container."""
    token = get_token(client)
    # Prendi un container esistente
    containers = client.get("/docker/containers/local", headers={"Authorization": f"Bearer {token}"}).json()
    if containers:
        cid = containers[0]["id"]
        # Restart
        res = client.post(f"/docker/container/restart/local/{cid}", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        # Stop
        res = client.post(f"/docker/container/stop/local/{cid}", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        # Remove (attenzione: rimuove il container!)
        # res = client.post(f"/docker/container/remove/local/{cid}", headers={"Authorization": f"Bearer {token}"})
        # assert res.status_code == 200