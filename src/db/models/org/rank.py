from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, TimestampMixin, UUIDMixing

if TYPE_CHECKING:
    from db.models.users.user import User


class Rank(Base, UUIDMixing, TimestampMixin):
    __tablename__ = "ranks"
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    code: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)

    users: Mapped[list["User"]] = relationship(
        "User", back_populates="rank", lazy="selectin"
    )
