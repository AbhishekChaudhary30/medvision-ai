"""Configuration tests."""

from app.core.config import Settings


def test_basic_configuration_loading(monkeypatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("LOG_LEVEL", "debug")

    settings = Settings()

    assert settings.environment == "test"
    assert settings.log_level == "DEBUG"
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.database_url.startswith("sqlite://") or settings.database_url.startswith("postgresql+psycopg://")
