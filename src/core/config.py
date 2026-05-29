import os
from functools import cache
from pathlib import Path
from typing import Any, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

ENV_FILE_PATH = (
    {
        "local": ".env",
        "ci": ".env.ci",
        "test": ".env.test",
    }
).get(os.getenv("ENV", "local"), ".env")


class Settings(BaseSettings):
    """
    These parameters can be configured with environment variables.
    """

    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
        enable_decoding=False,
    )

    # App core
    APP_TITLE: str = "TTM"
    APP_NAME: str = "fastapi-backend"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Production-ready Fastapi backend"

    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    APP_RELOAD: bool = True

    ENV: Literal["local", "test", "ci", "dev", "prod"] = "local"

    ROOT_PATH: str = ""

    DEBUG: bool = False

    SECRET_KEY: str

    # SECURITY / CORS
    ALLOWED_HOSTS: list[str] = Field(default_factory=lambda: ["*"])
    CORS_ORIGINS: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # POSTGRES
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    POSTGRES_ECHO: bool = True

    # JWT
    JWT_ALGORITHM: str = "HS256"

    JWT_ISSUER: str = "fastapi-backend"
    JWT_AUDIENCE: str = "fastapi-client"

    JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # PASSWORD HASHING
    BCRYPT_ROUNDS: int = 12

    # REDIS
    REDIS_URL: str = "redis://redis:6379/0"

    # RATE LIMIT
    RATE_LIMIT_ENABLED: bool = True

    RATE_LIMIT_STORAGE_URL: str = "memory://"

    RATE_LIMIT_DEFAULT: str = "10/minute"
    RATE_LIMIT_LOGIN: str = "10/minute"

    RATE_LIMIT_TRUSTED_PROXIES: str = ""

    # CELERY
    CELERY_BROKER_URL: str = "redis://redis:6379/0"

    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"

    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"

    CELERY_ACCEPT_CONTENT: list[str] = Field(default_factory=lambda: ["json"])

    CELERY_TIMEZONE: str = "UTC"

    # EMAIL
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_FROM: str
    SMTP_USER: str
    SMTP_PASSWORD: str

    # MONITORING
    SENTRY_DSN: str | None = None
    PROMETHEUS_METRICS_KEY: str | None = None

    # Logging
    LOG_LEVEL: str = "INFO"

    LOG_JSON: bool = False

    LOG_INCLUDE_REQUEST_ID: bool = True

    LOG_ENQUEUE: bool = False

    SERVICE_NAME: str = "fastapi-backend"

    # Audit
    AUDIT_ENABLED: bool = True

    # Alerts Default
    ALERT_TRANSFER_DAYS_LIMIT: int = 7
    ALERT_REPAIR_LOOKBACK_DAYS: int = 90
    ALERT_REPAIR_THRESHOLD: int = 3
    ALERT_REPAIR_THRESHOLD_MULTIPLIER: int = 2
    ALERT_INACTIVE_ASSET_DAYS: int = 60
    ALERT_OVERLOADED_USER_THRESHOLD: int = 10

    # Analytics
    ANALYTICS_SEARCH_MAX_LENGTH: int = 100

    # ========== FILE STORAGE SYSTEM ==========
    STORAGE_ROOT_DIR: str = "storage"
    STORAGE_URL_PREFIX: str = "http://localhost:8000/storage"  # or "/storage"

    STORAGE_DEFAULT_MAX_SIZE_MB: int = 10
    STORAGE_DEFAULT_ALLOWED_MIMETYPES: list[str] = Field(
        default_factory=lambda: [
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp",
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]
    )

    STORAGE_AVATAR_MAX_SIZE_MB: int = 2
    STORAGE_AVATAR_ALLOWED_MIMETYPES: list[str] = Field(
        default_factory=lambda: [
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/gif",
            "image/webp",
        ]
    )
    STORAGE_AVATAR_FOLDER: str = "avatars"

    STORAGE_ASSET_IMAGE_MAX_SIZE_MB: int = 5
    STORAGE_ASSET_IMAGE_ALLOWED_MIMETYPES: list[str] = Field(
        default_factory=lambda: ["image/jpeg", "image/png", "image/gif", "image/webp"]
    )
    STORAGE_ASSET_IMAGE_FOLDER: str = "assets"

    STORAGE_DOCUMENT_MAX_SIZE_MB: int = 15
    STORAGE_DOCUMENT_ALLOWED_MIMETYPES: list[str] = Field(
        default_factory=lambda: [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ]
    )
    STORAGE_DOCUMENT_FOLDER: str = "documents"

    STORAGE_FILENAME_MAX_LENGTH: int = 255
    STORAGE_KEEP_ORIGINAL_NAME: bool = False
    STORAGE_VIRUS_SCAN_ENABLED: bool = False
    STORAGE_VIRUS_SCAN_URL: str | None = None

    # ========== VALIDATORS ==========
    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug_flag(cls, value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug"}:
                return True
            if normalized in {
                "0",
                "false",
                "no",
                "off",
                "release",
                "prod",
                "production",
            }:
                return False
        return bool(value)

    @field_validator(
        "ALLOWED_HOSTS",
        "CORS_ORIGINS",
        "STORAGE_DEFAULT_ALLOWED_MIMETYPES",
        "STORAGE_AVATAR_ALLOWED_MIMETYPES",
        "STORAGE_ASSET_IMAGE_ALLOWED_MIMETYPES",
        "STORAGE_DOCUMENT_ALLOWED_MIMETYPES",
        "CELERY_ACCEPT_CONTENT",
        mode="before",
    )
    @classmethod
    def parse_csv_list(cls, value: Any) -> list[str]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return []

    # ========== DATABASE URLS ==========
    @property
    def postgres_async_url(self) -> str:
        return str(
            URL.build(
                scheme="postgresql+asyncpg",
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                user=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                path=f"/{self.POSTGRES_DB}",
            )
        )

    @property
    def postgres_sync_url(self) -> str:
        return str(
            URL.build(
                scheme="postgresql+psycopg",
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                user=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                path=f"/{self.POSTGRES_DB}",
            )
        )


@cache
def get_settings() -> Settings:
    return Settings()
