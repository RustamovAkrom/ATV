from typing import TYPE_CHECKING
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Boolean, DateTime, Index

from db.base import Base, UUIDMixing

if TYPE_CHECKING:
    from db.models.users.user import User


class RefreshToken(Base, UUIDMixing):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )

    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship(lazy="selectin")

    __table_args__ = (
        Index("idx_refresh_user_active", "user_id", "is_revoked"),
    )
