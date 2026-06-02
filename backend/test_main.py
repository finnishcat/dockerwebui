from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def get_token():
    res = client.post("/auth/login", data={"username": "admin", "password": "admin"})
    assert res.status_code == 200
    return res.json()["access_token"]


def test_login():
    res = client.post("/auth/login", data={"username": "admin", "password": "admin"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_invalid():
    res = client.post("/auth/login", data={"username": "admin", "password": "wrong"})
    assert res.status_code == 400


def test_list_containers():
    token = get_token()
    res = client.get("/docker/containers/local", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_list_images():
    token = get_token()
    res = client.get("/docker/images/local", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_unauthorized():
    res = client.get("/docker/containers/local")
    assert res.status_code == 401


def test_invalid_node():
    token = get_token()
    res = client.get("/docker/containers/nonexistent", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 404


def test_invalid_image_name():
    token = get_token()
    res = client.post(
        "/docker/image/pull/local",
        json={"image": "invalid image name !!!"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 400


def test_invalid_token():
    res = client.get("/docker/containers/local", headers={"Authorization": "Bearer invalidtoken"})
    assert res.status_code == 401


def test_save_image_not_found():
    token = get_token()
    res = client.get("/docker/image/save/local/nonexistent", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 404


def test_load_image_no_file():
    token = get_token()
    res = client.post("/docker/image/load/local", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 422  # missing file
