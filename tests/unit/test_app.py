"""Application startup tests."""

from app.main import create_app


def test_application_startup_registers_versioned_health_route() -> None:
    application = create_app()
    paths = set(application.openapi()["paths"])

    assert "/api/v1/health" in paths
    assert application.title == "MedVision AI"
