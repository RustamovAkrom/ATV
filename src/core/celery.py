# src/core/celery.py

from celery import Celery

from core.config import get_settings
from core.logger import configure_logger

logger = configure_logger()
settings = get_settings()

celery_app = Celery(
    settings.APP_NAME,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

def autodiscover_module_tasks() -> None:
    """
    Auto-discover tasks inside src/tasks/*
    """
    packages = ["tasks"]

    logger.info("Registering celery tasks", packages=packages)
    celery_app.autodiscover_tasks(packages)


autodiscover_module_tasks()
