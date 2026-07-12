import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from backend.utils.exceptions import AppError

logger = logging.getLogger(__name__)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Convert known application errors into JSON responses."""
    logger.exception("Application error at %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Convert unexpected exceptions into safe JSON responses."""
    logger.exception("Unhandled error at %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."},
    )
