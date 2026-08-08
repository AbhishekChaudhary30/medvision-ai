"""Application exception foundation."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger

logger = get_logger(__name__)


class AppException(Exception):
    """Base exception for controlled application errors."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "application_error",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    """Build a predictable API error response."""
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    """Handle controlled application exceptions."""
    return error_response(exc.status_code, exc.code, exc.message)


async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Normalize framework HTTP exceptions."""
    return error_response(exc.status_code, "http_error", str(exc.detail))


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Hide internal details from API clients while logging server failures."""
    logger.exception("Unhandled exception during request %s %s", request.method, request.url.path)
    return error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "internal_server_error",
        "An unexpected error occurred.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register application exception handlers."""
    app.add_exception_handler(AppException, app_exception_handler)  # type: ignore
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore
    app.add_exception_handler(Exception, unhandled_exception_handler)
