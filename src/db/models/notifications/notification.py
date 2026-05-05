from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base, UUIDMixing


class Notification(Base, UUIDMixing):
    __tablename__ = "notifications"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    type: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(String(1000))

    data: Mapped[dict] = mapped_column(JSON, default=dict)

    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user = relationship("User", lazy="selectin")

    __table_args__ = (Index("idx_notifications_user_unread", "user_id", "is_read"),)
