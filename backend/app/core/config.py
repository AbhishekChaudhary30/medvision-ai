"""Application configuration."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["local", "development", "test", "staging", "production"]


class Settings(BaseSettings):
    """Typed environment-driven application settings."""

    app_name: str = "MedVision AI"
    app_version: str = "0.1.0"
    environment: Environment = "local"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    database_url: str = Field(
        default="postgresql+psycopg://medvision_app@localhost:5432/medvision_ai",
        description="SQLAlchemy PostgreSQL database URL.",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("api_v1_prefix")
    @classmethod
    def validate_api_prefix(cls, value: str) -> str:
        """Ensure the API prefix is absolute and stable."""
        if not value.startswith("/"):
            msg = "API_V1_PREFIX must start with '/'."
            raise ValueError(msg)
        return value.rstrip("/") or "/"

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        """Normalize and validate log level values."""
        normalized = value.upper()
        allowed = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}
        if normalized not in allowed:
            msg = f"LOG_LEVEL must be one of: {', '.join(sorted(allowed))}."
            raise ValueError(msg)
        return normalized


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
