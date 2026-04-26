from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, Boolean, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base, UUIDMixing
from db.models.enums import ApprovalStatus


class ApprovalRequest(Base, UUIDMixing):
    __tablename__ = "approval_requests"

    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_by = relationship("User", foreign_keys=[created_by_id], lazy="selectin")
    approved_by = relationship("User", foreign_keys=[approved_by_id], lazy="selectin")
