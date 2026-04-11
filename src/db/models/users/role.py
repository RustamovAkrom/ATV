from typing import List, TYPE_CHECKING
from sqlalchemy import Column, String, Text, Table, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import relationship, Mapped, mapped_column
from db.base import Base, UUIDMixing
from db.models.users.associations import role_permissions

if TYPE_CHECKING:
    from .permission import Permission


class Role(Base, UUIDMixing):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)

    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin"
    )
