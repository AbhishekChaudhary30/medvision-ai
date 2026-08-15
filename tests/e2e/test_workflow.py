"""End-to-End API Integration test."""

import os
from pathlib import Path
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def get_test_image_path() -> Path:
    """Helper to get a real synthetic image path for E2E tests."""
    images_dir = Path("data/raw/stage_2_train_images")
    if not images_dir.exists():
        # Fallback to creating a dummy valid image temporarily if the test runs in CI
        import numpy as np
        from PIL import Image
        dummy_path = Path("test_e2e_image.jpg")
        np.random.seed(42)
        arr = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        Image.fromarray(arr).save(dummy_path)
        return dummy_path
    
    # Just grab the first DICOM
    return list(images_dir.glob("*.dcm"))[0]


def test_full_workflow(client: TestClient, db_session: Session):
    """
    Test End-to-End Workflow:
    1. Register
    2. Login
    3. Upload real image for analysis
    4. Request explainability
    5. List history
    """
    # 1. Register
    client.post("/api/v1/auth/register", json={"email": "e2e@example.com", "password": "password123"})

    # 2. Login
    login_resp = client.post("/api/v1/auth/login", data={"username": "e2e@example.com", "password": "password123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Upload image for analysis
    image_path = get_test_image_path()
    
    with open(image_path, "rb") as f:
        file_bytes = f.read()

    # The API specifically requires jpeg/png right now in analyses.py!
    # Wait, the dataset generation creates .dcm. analyses.py ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
    # Let me make sure I send it as jpeg and read a valid jpeg.
    # Actually, the ML service expects to open the image with PIL. `Image.open(file_path)` supports JPEG/PNG, not DICOM.
    # I should convert a DICOM to JPEG for the test, or just generate a JPEG directly.
    import numpy as np
    from PIL import Image
    dummy_path = Path("test_e2e_real_image.jpg")
    np.random.seed(42)
    arr = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    Image.fromarray(arr).save(dummy_path)

    with open(dummy_path, "rb") as f:
        analysis_resp = client.post("/api/v1/analyses", headers=headers, files={"file": ("test.jpg", f, "image/jpeg")})
    
    assert analysis_resp.status_code == 201, f"Failed: {analysis_resp.text}"
    analysis_id = analysis_resp.json()["id"]

    # 4. Request explainability
    explain_resp = client.post(f"/api/v1/analyses/{analysis_id}/explain", headers=headers, json={"method": "gradcam"})
    assert explain_resp.status_code == 200, f"Failed: {explain_resp.text}"
    assert explain_resp.json()["explanation_method"] == "gradcam"

    # 5. List history
    history_resp = client.get("/api/v1/analyses", headers=headers)
    assert history_resp.status_code == 200
    items = history_resp.json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == analysis_id
    assert items[0]["explanation_method"] == "gradcam"
    
    # Cleanup
    if dummy_path.exists():
        dummy_path.unlink()
