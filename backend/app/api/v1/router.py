"""Version 1 API router."""

from fastapi import APIRouter

from app.core.config import get_settings

api_router = APIRouter()


@api_router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return API health status."""
    settings = get_settings()
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.environment,
        "version": settings.app_version,
    }
