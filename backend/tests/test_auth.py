"""
Auth endpoint tests for AI Academic Roadmap API.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_user_data():
    return {
        "full_name": "Test Student",
        "email": "test@example.com",
        "password": "SecurePassword123!"
    }


class TestAuthRegister:
    """Tests for POST /api/v1/auth/register"""

    def test_register_success(self, client: TestClient, test_user_data):
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert data["data"]["user"]["email"] == test_user_data["email"]

    def test_register_duplicate_email(self, client: TestClient, test_user_data):
        client.post("/api/v1/auth/register", json=test_user_data)
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == 409

    def test_register_invalid_email(self, client: TestClient):
        response = client.post("/api/v1/auth/register", json={
            "full_name": "Test",
            "email": "not-an-email",
            "password": "SecurePassword123!"
        })
        assert response.status_code == 422

    def test_register_weak_password(self, client: TestClient):
        response = client.post("/api/v1/auth/register", json={
            "full_name": "Test",
            "email": "test2@example.com",
            "password": "123"
        })
        assert response.status_code == 422


class TestAuthLogin:
    """Tests for POST /api/v1/auth/login"""

    def test_login_success(self, client: TestClient, test_user_data):
        client.post("/api/v1/auth/register", json=test_user_data)
        response = client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]

    def test_login_wrong_password(self, client: TestClient, test_user_data):
        client.post("/api/v1/auth/register", json=test_user_data)
        response = client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": "WrongPassword!"
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        response = client.post("/api/v1/auth/login", json={
            "email": "nobody@example.com",
            "password": "Password123!"
        })
        assert response.status_code == 401
