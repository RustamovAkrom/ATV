from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from db.mixins import TimestampMixin, UUIDMixing
from db.models.enums import ApprovalStatus

if TYPE_CHECKING:
    from db.models.users.user import User


class ApprovalRequest(Base, UUIDMixing, TimestampMixin):
    __tablename__ = "approval_requests"

    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSON), default=lambda: {}, nullable=False
    )
    status: Mapped[ApprovalStatus] = mapped_column(
        SAEnum(
            ApprovalStatus,
            name="approval_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=ApprovalStatus.PENDING,
        nullable=False,
    )
    created_by_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    approved_by_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    executed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_by: Mapped["User"] = relationship(
        "User", foreign_keys=[created_by_id], lazy="selectin"
    )
    approved_by: Mapped["User"] = relationship(
        "User", foreign_keys=[approved_by_id], lazy="selectin"
    )

    __table_args__ = (Index("ix_approval_status_created", "status", "created_at"),)
