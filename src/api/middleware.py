"""Middleware for FastAPI application.

This module provides middleware for logging, timing, and error handling.
"""

import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from src.utils.logger import get_logger
from src.utils.config import get_settings

logger = get_logger(__name__)


async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """Log all incoming requests and responses.

    Args:
        request: FastAPI request
        call_next: Next middleware/handler

    Returns:
        Response
    """
    logger.info(
        "Request received",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else None,
        },
    )

    response = await call_next(request)

    logger.info(
        "Response sent",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
        },
    )

    return response


async def timing_middleware(request: Request, call_next: Callable) -> Response:
    """Measure request processing time.

    Args:
        request: FastAPI request
        call_next: Next middleware/handler

    Returns:
        Response with timing header
    """
    start_time = time.time()

    response = await call_next(request)

    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time"] = str(process_time)

    logger.debug(
        "Request processed",
        extra={
            "path": request.url.path,
            "process_time_ms": process_time,
        },
    )

    return response


async def error_handling_middleware(request: Request, call_next: Callable) -> Response:
    """Handle errors and return proper JSON responses.

    Args:
        request: FastAPI request
        call_next: Next middleware/handler

    Returns:
        Response or error JSON
    """
    try:
        return await call_next(request)

    except Exception as e:
        logger.error(
            "Unhandled error",
            extra={
                "path": request.url.path,
                "method": request.method,
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )


def setup_middleware(app: FastAPI) -> None:
    """Setup all middleware for the application.

    Args:
        app: FastAPI application
    """
    settings = get_settings()

    app.middleware("http")(error_handling_middleware)
    app.middleware("http")(timing_middleware)
    app.middleware("http")(logging_middleware)

    logger.info("Middleware configured")
