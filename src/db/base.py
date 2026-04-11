from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import uuid
from db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IDMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class UUIDMixing:
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
