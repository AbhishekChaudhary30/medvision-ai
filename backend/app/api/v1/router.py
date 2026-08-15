"""Version 1 API router."""

from fastapi import APIRouter

from app.api.v1.endpoints import admin, analyses, auth, models, batch
from app.core.config import get_settings

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(analyses.router, prefix="/analyses", tags=["analyses"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(batch.router, prefix="/batch", tags=["batch"])


@api_router.get("/health", tags=["health"])
def health_check() -> dict:
    """Basic health check endpoint."""
    settings = get_settings()
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.environment,
        "version": settings.app_version,
    }
