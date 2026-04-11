from typing import TYPE_CHECKING
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Boolean, DateTime

from db.base import Base, UUIDMixing

if TYPE_CHECKING:
    from .users import User


class RefreshToken(Base, UUIDMixing):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    is_revoked: Mapped[bool] = mapped_column(default=False)

    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # relationships
    user: Mapped["User"] = relationship(lazy="selectin")
