"""End-to-End API Integration test."""

from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@patch("app.api.v1.endpoints.analyses.process_and_predict")
@patch("app.api.v1.endpoints.analyses.process_explainability")
@patch("app.api.v1.endpoints.analyses.save_upload_file")
def test_full_workflow(mock_save, mock_explain, mock_predict, client: TestClient, db_session: Session, tmp_path):
    """
    Test End-to-End Workflow:
    1. Register
    2. Login
    3. Upload image for analysis
    4. Request explainability
    5. List history
    """
    
    # Mocks
    mock_save.return_value = tmp_path / "e2e.jpg"
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
    mock_explain.return_value = {
        "heatmap": [[0.1, 0.2], [0.3, 0.4]],
        "overlay_image_base64": "dummybase64data",
        "method": "gradcam",
        "target_layer": "layer4"
    }
    
    # 1. Register
    client.post(
        "/api/v1/auth/register",
        json={"email": "e2e@example.com", "password": "password123"}
    )
    
    # 2. Login
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "e2e@example.com", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Upload image for analysis
    analysis_resp = client.post(
        "/api/v1/analyses",
        headers=headers,
        files={"file": ("test.jpg", b"dummy", "image/jpeg")}
    )
    assert analysis_resp.status_code == 201
    analysis_id = analysis_resp.json()["id"]
    
    # 4. Request explainability
    explain_resp = client.post(
        f"/api/v1/analyses/{analysis_id}/explain",
        headers=headers,
        json={"method": "gradcam"}
    )
    assert explain_resp.status_code == 200
    assert explain_resp.json()["explanation_method"] == "gradcam"
    
    # 5. List history
    history_resp = client.get("/api/v1/analyses", headers=headers)
    assert history_resp.status_code == 200
    items = history_resp.json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == analysis_id
    assert items[0]["explanation_method"] == "gradcam"
