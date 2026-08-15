"""Analysis API tests."""

import os
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def get_token(client: TestClient, email: str = "user@example.com") -> str:
    """Helper to get a token."""
    client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})
    response = client.post("/api/v1/auth/login", data={"username": email, "password": "password123"})
    return response.json()["access_token"]


def create_dummy_jpeg(path: Path):
    import numpy as np
    from PIL import Image
    np.random.seed(42)
    arr = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    Image.fromarray(arr).save(path)


def test_submit_analysis(client: TestClient, db_session: Session):
    token = get_token(client)
    
    dummy_path = Path("test_api_image.jpg")
    create_dummy_jpeg(dummy_path)

    with open(dummy_path, "rb") as f:
        response = client.post(
            "/api/v1/analyses", headers={"Authorization": f"Bearer {token}"}, files={"file": ("test.jpg", f, "image/jpeg")}
        )

    assert response.status_code == 201
    data = response.json()
    assert data["predicted_class"] in ["PNEUMONIA", "NORMAL"]
    assert "id" in data
    
    if dummy_path.exists():
        dummy_path.unlink()


def test_list_analyses(client: TestClient, db_session: Session):
    token = get_token(client, "list@example.com")
    
    dummy_path = Path("test_api_list.jpg")
    create_dummy_jpeg(dummy_path)

    with open(dummy_path, "rb") as f:
        client.post("/api/v1/analyses", headers={"Authorization": f"Bearer {token}"}, files={"file": ("test.jpg", f, "image/jpeg")})

    response = client.get("/api/v1/analyses", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["predicted_class"] in ["PNEUMONIA", "NORMAL"]
    
    if dummy_path.exists():
        dummy_path.unlink()
