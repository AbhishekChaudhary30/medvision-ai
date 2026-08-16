"""Authentication API tests."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_register_user(client: TestClient, db_session: Session):
    response = client.post("/api/v1/auth/register", json={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data


def test_register_duplicate_user(client: TestClient, db_session: Session):
    client.post("/api/v1/auth/register", json={"email": "duplicate@example.com", "password": "password123"})
    response = client.post("/api/v1/auth/register", json={"email": "duplicate@example.com", "password": "password123"})
    assert response.status_code == 409


def test_login_user(client: TestClient, db_session: Session):
    client.post("/api/v1/auth/register", json={"email": "login@example.com", "password": "password123"})
    response = client.post("/api/v1/auth/login", data={"username": "login@example.com", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_get_current_user(client: TestClient, db_session: Session):
    client.post("/api/v1/auth/register", json={"email": "me@example.com", "password": "password123"})
    login_response = client.post("/api/v1/auth/login", data={"username": "me@example.com", "password": "password123"})
    token = login_response.json()["access_token"]

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"
