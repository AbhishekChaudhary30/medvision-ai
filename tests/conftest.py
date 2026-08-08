"""Shared test fixtures for MedVision AI API testing."""

import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Setup test DB (In-memory SQLite for speed)
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.db.base import Base
from app.db.session import get_db
from app.main import app

# Import all models so Base.metadata knows about them
from app.models.user import User  # noqa
from app.models.analysis import Analysis, AnalysisArtifact  # noqa

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Dependency override for test DB."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """Test client fixture."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def db_session():
    """Provides a fresh database session for a test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
