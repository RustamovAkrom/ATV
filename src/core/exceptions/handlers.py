# src/core/exceptions/handlers.py

import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.logger import configure_logger

from .base import APIException
from .errors import InternalError


def register_exception_handlers(app: FastAPI) -> None:
    logger = configure_logger()

    # 🔴 APIException
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        trace_id = str(uuid.uuid4())

        logger.warning(
            "API exception",
            extra={
                "trace_id": trace_id,
                "path": request.url.path,
                "code": exc.code,
                "detail": exc.detail,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(trace_id),
        )

    # 🔴 Validation (Pydantic)
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        trace_id = str(uuid.uuid4())

        logger.warning(
            "Validation error",
            extra={
                "trace_id": trace_id,
                "path": request.url.path,
                "errors": exc.errors(),
            },
        )

        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Invalid request data",
                    "details": exc.errors(),
                    "trace_id": trace_id,
                }
            },
        )

    # 🔴 FastAPI HTTPException
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        trace_id = str(uuid.uuid4())

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "http_error",
                    "message": exc.detail,
                    "trace_id": trace_id,
                }
            },
        )

    # 🔴 UNEXPECTED ERROR (CRITICAL)
    @app.exception_handler(Exception)
    async def unexpected_exception_handler(request: Request, exc: Exception):
        trace_id = str(uuid.uuid4())

        logger.exception(
            "Unhandled exception",
            extra={
                "trace_id": trace_id,
                "path": request.url.path,
            },
        )

        error = InternalError()

        return JSONResponse(
            status_code=error.status_code,
            content=error.to_dict(trace_id),
        )
