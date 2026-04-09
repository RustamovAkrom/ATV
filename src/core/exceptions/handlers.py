from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.logger import configure_logger

from .base import APIException


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers.
    """
    logger = configure_logger()

    @app.exception_handler(APIException)
    async def api_exception_handler(
        request: Request,
        exc: APIException,
    ) -> JSONResponse:
        logger.warning(
            "API exception",
            extra={
                "path": request.url.path,
                "code": exc.code,
                "detail": exc.detail,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "code": exc.code,
                "variables": exc.values,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.warning(
            "Validation error",
            extra={"path": request.url.path},
        )

        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation error.",
                "code": "validation_error",
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "code": "http_error",
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception(
            "Unhandled exception",
            extra={"path": request.url.path},
        )

        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error.",
                "code": "internal_error",
            },
        )
