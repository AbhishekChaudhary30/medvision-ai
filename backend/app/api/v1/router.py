"""Version 1 API router."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, admin, analyses

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(analyses.router, prefix="/analyses", tags=["analyses"])


@api_router.get("/health", tags=["health"])
def health_check() -> dict:
    """Basic health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}
