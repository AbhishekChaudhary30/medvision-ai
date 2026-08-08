"""FastAPI application entrypoint."""

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    configure_logging(settings.log_level)

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Research and educational clinical decision-support prototype.",
    )
    register_exception_handlers(application)
    application.include_router(api_router, prefix=settings.api_v1_prefix)

    logger.info(
        "Configured %s API %s for %s",
        settings.app_name,
        settings.app_version,
        settings.environment,
    )
    return application


app = create_app()
