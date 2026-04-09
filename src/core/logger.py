from __future__ import annotations

import sys
from pathlib import Path

import loguru
from loguru import logger

from core.config import get_settings


def configure_logger() -> loguru.Logger:
    """
    Production-safe logger configuration.

    - stdout logging (default, Docker-friendly)
    - optional file logging via LOG_PATH
    - no filesystem crashes
    """

    settings = get_settings()

    # remove default handlers
    logger.remove()

    level = "DEBUG" if settings.DEBUG else "INFO"

    # STDOUT (MAIN)
    logger.add(
        sys.stdout,
        level=level,
        colorize=settings.DEBUG,
        backtrace=settings.DEBUG,
        diagnose=settings.DEBUG,
        enqueue=True,  # important for async environments
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
            "- <level>{message}</level>"
        ),
    )

    # OPTIONAL FILE LOGGING
    log_path: str | None = getattr(settings, "LOG_PATH", None)

    if log_path:
        try:
            log_dir = Path(log_path)
            log_dir.mkdir(parents=True, exist_ok=True)

            # general logs
            logger.add(
                log_dir / "app.log",
                rotation="10 MB",
                retention="10 days",
                enqueue=True,
                serialize=not settings.DEBUG,
            )

            # error logs
            logger.add(
                log_dir / "errors.log",
                level="ERROR",
                rotation="5 MB",
                retention="30 days",
                compression="zip",
                enqueue=True,
                backtrace=True,
                diagnose=True,
                serialize=True,
            )

        except OSError:
            # fallback: ignore file logging in read-only FS
            logger.warning("File logging disabled (read-only filesystem)")

    return logger
