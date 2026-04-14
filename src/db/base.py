import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, validates

from db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IDMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


# Mixins
class UUIDMixin:
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )


# Backward-compatible alias to avoid broad import churn.
UUIDMixing = UUIDMixin


class StatusMixin:
    STATUS_ENUM: Any = None

    status: Mapped[str] = mapped_column(String(50), nullable=False)

    @validates("status")
    def validate_status(self, key: str, value: str) -> str:
        if value not in [e.value for e in self.STATUS_ENUM]:
            raise ValueError(f"Invalid status: {value}")
        return value
