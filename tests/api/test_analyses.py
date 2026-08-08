"""Analysis API tests."""

from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def get_token(client: TestClient, email: str = "user@example.com") -> str:
    """Helper to get a token."""
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123"}
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "password123"}
    )
    return response.json()["access_token"]


@patch("app.api.v1.endpoints.analyses.process_and_predict")
@patch("app.api.v1.endpoints.analyses.save_upload_file")
def test_submit_analysis(mock_save, mock_predict, client: TestClient, db_session: Session, tmp_path):
    token = get_token(client)
    
    mock_save.return_value = tmp_path / "dummy.jpg"
    mock_predict.return_value = {
        "model_version": "v1.0",
        "model_architecture": "custom_cnn",
        "predicted_class": "PNEUMONIA",
        "predicted_class_index": 1,
        "probability_normal": 0.1,
        "probability_pneumonia": 0.9,
        "confidence": 0.9,
        "threshold": 0.5,
        "uncertainty_status": "LOW",
        "entropy": 0.2,
        "margin": 0.8,
        "calibration_status": "UNAVAILABLE",
        "inference_time": 150.0,
    }
    
    response = client.post(
        "/api/v1/analyses",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.jpg", b"dummy image content", "image/jpeg")}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["predicted_class"] == "PNEUMONIA"
    assert "id" in data


@patch("app.api.v1.endpoints.analyses.process_and_predict")
@patch("app.api.v1.endpoints.analyses.save_upload_file")
def test_list_analyses(mock_save, mock_predict, client: TestClient, db_session: Session, tmp_path):
    token = get_token(client, "list@example.com")
    
    mock_save.return_value = tmp_path / "dummy.jpg"
    mock_predict.return_value = {
        "model_version": "v1.0",
        "model_architecture": "custom_cnn",
        "predicted_class": "NORMAL",
        "predicted_class_index": 0,
        "probability_normal": 0.8,
        "probability_pneumonia": 0.2,
        "confidence": 0.8,
        "threshold": 0.5,
        "uncertainty_status": "LOW",
        "entropy": 0.3,
        "margin": 0.6,
        "calibration_status": "UNAVAILABLE",
        "inference_time": 100.0,
    }
    
    client.post(
        "/api/v1/analyses",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.jpg", b"dummy image content", "image/jpeg")}
    )
    
    response = client.get(
        "/api/v1/analyses",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["predicted_class"] == "NORMAL"
