from datetime import datetime

from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IDMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
