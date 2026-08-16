"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.services.ml_service import initialize_engine

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # initialize_engine(strict=False)  # Disabled to fix Render Free tier timeout
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    configure_logging(settings.log_level, settings.environment)

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Research and educational clinical decision-support prototype.",
        lifespan=lifespan,
    )
    register_exception_handlers(application)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_origin_regex="https://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router, prefix=settings.api_v1_prefix)

    # Expose Prometheus metrics
    Instrumentator().instrument(application).expose(application, endpoint="/metrics")

    logger.info(
        "Configured %s API %s for %s",
        settings.app_name,
        settings.app_version,
        settings.environment,
    )
    return application


app = create_app()
