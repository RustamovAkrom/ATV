from __future__ import annotations

import sys
from loguru import logger
from core.config import get_settings

settings = get_settings()


def _inject_request_id(record):
    if settings.LOG_INCLUDE_REQUEST_ID:
        record["extra"].setdefault("request_id", "-")
    return record


def configure_logger():
    logger.remove()

    logger.configure(
        patcher=_inject_request_id
    )

    if settings.LOG_INCLUDE_REQUEST_ID:
        log_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level} | "
            "{extra[request_id]} | "
            "{name}:{function}:{line} - {message}"
        )
    else:
        log_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level} | "
            "{name}:{function}:{line} - {message}"
        )

    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        enqueue=True,
        backtrace=settings.DEBUG,
        diagnose=settings.DEBUG,
        colorize=settings.DEBUG and not settings.LOG_JSON,
        serialize=settings.LOG_JSON,
        format=log_format,
    )

    return logger


def bind_logger(request_id: str):
    return logger.bind(request_id=request_id)
