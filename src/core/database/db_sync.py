from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import get_settings


@lru_cache
def get_db_sync_engine():
    settings = get_settings()

    return create_engine(
        settings.postgres_sync_url,
        echo=settings.POSTGRES_ECHO,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300,
    )


@lru_cache
def get_sync_session_factory() -> sessionmaker[Session]:
    return sessionmaker(
        bind=get_db_sync_engine(),
        expire_on_commit=False,
    )
