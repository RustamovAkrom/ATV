from typing import List, TYPE_CHECKING
from db.base import Base, UUIDMixing
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

if TYPE_CHECKING:
    from .role import Role

class Permission(Base, UUIDMixing):
    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(String(150), unique=True)
    name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None]

    roles: Mapped[List["Role"]] = relationship(
        secondary="role_permissions",
        back_populates="permissions",
        lazy="selectin"
    )
