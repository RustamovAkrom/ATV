import uuid

from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.logger import configure_logger
from core.slowapi import rate_limit_exceeded_handler

from .base import APIException
from .errors import Conflict, InternalError, ValidationError


def configure_exception_handlers(app: FastAPI) -> None:
    logger = configure_logger()

    # RATE LIMIT
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    # CUSTOM API EXCEPTION
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

    # REQUEST VALIDATION
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
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
            status_code=400,
            content=jsonable_encoder(
                {
                    "error": {
                        "code": "validation_error",
                        "message": "Invalid request data",
                        "details": exc.errors(),
                        "trace_id": trace_id,
                    }
                }
            ),
        )

    # HTTP EXCEPTION
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        trace_id = str(uuid.uuid4())

        logger.warning(
            "HTTP exception",
            extra={
                "trace_id": trace_id,
                "path": request.url.path,
                "status_code": exc.status_code,
                "detail": exc.detail,
            },
        )

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

    # DATABASE EXCEPTIONS
    @app.exception_handler(IntegrityError)
    async def db_exception_handler(request: Request, exc: IntegrityError):
        trace_id = str(uuid.uuid4())

        orig = exc.orig

        if isinstance(orig, UniqueViolationError):
            error = Conflict(detail="Resource already exists")

        elif isinstance(orig, ForeignKeyViolationError):
            error = ValidationError(detail="Invalid reference")

        else:
            error = ValidationError(detail="Database error")

        logger.warning(
            "Database error",
            extra={
                "trace_id": trace_id,
                "path": request.url.path,
                "error": str(orig),
            },
        )

        return JSONResponse(
            status_code=error.status_code,
            content=error.to_dict(trace_id),
        )

    # UNHANDLED EXCEPTIONS
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
