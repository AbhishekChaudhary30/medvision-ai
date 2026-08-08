"""Health endpoint tests."""

from fastapi.testclient import TestClient


from app.core.config import get_settings

def test_health_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "MedVision AI",
        "environment": get_settings().environment,
        "version": "0.1.0",
    }
