"""Shared pytest configuration."""

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://medvision_app@localhost:5432/medvision_ai_test",
)

from app.main import create_app  # noqa: E402


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Return a test client for the FastAPI application."""
    with TestClient(create_app()) as test_client:
        yield test_client
