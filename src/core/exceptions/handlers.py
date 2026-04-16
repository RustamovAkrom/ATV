import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.encoders import jsonable_encoder
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError
from core.exceptions.errors import Conflict, ValidationError
from core.slowapi import rate_limit_exceeded_handler
from core.logger import configure_logger

from .base import APIException
from .errors import InternalError


def configure_exception_handlers(app: FastAPI) -> None:
    logger = configure_logger()

    # SlowAPI Exception Handler
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    # APIException
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
            content=jsonable_encoder({   # ✅ ВАЖНО
                "error": {
                    "code": "validation_error",
                    "message": "Invalid request data",
                    "details": exc.errors(),
                    "trace_id": trace_id,
                }
            }),
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

        return JSONResponse(
            status_code=error.status_code,
            content=error.to_dict(trace_id),
        )
