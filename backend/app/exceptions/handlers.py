import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Register centralized exception handlers mapping errors."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle incoming request validation errors (Pydantic / FastAPI)."""
        logger.warning(f"Request validation failed: {exc}")
        details = exc.errors()
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Input validation failed",
                    "details": details,
                },
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle standard HTTP exceptions."""
        logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": "HTTP_ERROR",
                    "message": str(exc.detail),
                    "details": None,
                },
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        _request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unexpected general application errors."""
        logger.exception(f"Unhandled system error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "details": None,
                },
            },
        )
