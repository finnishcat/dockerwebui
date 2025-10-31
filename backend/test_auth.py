"""
Comprehensive authentication tests for DockerWebUI backend.
"""
from fastapi.testclient import TestClient
from main import app
import json
import os

client = TestClient(app)

def setup_module(module):
    """Clean up users.json before running tests."""
    users_file = os.path.join(os.path.dirname(__file__), "users.json")
    if os.path.exists(users_file):
        os.remove(users_file)

def test_login_success():
    """Test successful login with valid credentials."""
    response = client.post("/auth/login", data={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    response = client.post("/auth/login", data={"username": "admin", "password": "wrong"})
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_login_missing_username():
    """Test login with missing username."""
    response = client.post("/auth/login", data={"username": "", "password": "admin"})
    assert response.status_code == 400

def test_login_missing_password():
    """Test login with missing password."""
    response = client.post("/auth/login", data={"username": "admin", "password": ""})
    assert response.status_code == 400

def test_login_nonexistent_user():
    """Test login with non-existent user."""
    response = client.post("/auth/login", data={"username": "nonexistent", "password": "password"})
    assert response.status_code == 401

def test_register_not_allowed():
    """Test that registration is not allowed when users exist."""
    response = client.post("/auth/register", json={"username": "newuser", "password": "newpassword123"})
    assert response.status_code == 403
    assert "Registration not allowed" in response.json()["detail"]

def test_protected_endpoint_without_token():
    """Test accessing protected endpoint without authentication."""
    response = client.get("/docker/containers/local")
    assert response.status_code == 401

def test_protected_endpoint_with_invalid_token():
    """Test accessing protected endpoint with invalid token."""
    response = client.get("/docker/containers/local", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401

def test_protected_endpoint_with_valid_token():
    """Test accessing protected endpoint with valid token."""
    # Get valid token
    login_response = client.post("/auth/login", data={"username": "admin", "password": "admin"})
    token = login_response.json()["access_token"]
    
    # Access protected endpoint
    response = client.get("/docker/containers/local", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
