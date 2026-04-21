import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, validates
from sqlalchemy.sql import func

from db.meta import meta
from utils.helpers import utc_now


class Base(DeclarativeBase):
    metadata = meta


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        server_default=func.now(),
        nullable=False
    )


class IDMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


# Mixins
class UUIDMixin:
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


# Backward-compatible alias to avoid broad import churn.
UUIDMixing = UUIDMixin


class StatusMixin:
    STATUS_ENUM: Any = None

    status: Mapped[str] = mapped_column(String(50), nullable=False)

    @validates("status")
    def validate_status(self, value: str) -> str:
        if self.STATUS_ENUM is None:
            raise TypeError("STATUS_ENUM is not configured")
        allowed = {e.value for e in self.STATUS_ENUM}
        if value not in allowed:
            raise ValueError(f"Invalid status: {value}")
        return value
