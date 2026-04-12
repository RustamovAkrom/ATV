from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, ForeignKey, Boolean, String

from db.base import Base, UUIDMixin, TimestampMixin


class PasswordReset(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "password_resets"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )

    is_used: Mapped[bool] = mapped_column(default=False)
