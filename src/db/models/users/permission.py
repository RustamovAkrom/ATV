from typing import List, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Table, Column, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID

from db.base import Base, UUIDMixing, TimestampMixin


if TYPE_CHECKING:
    from .user import User


role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class Role(Base, UUIDMixing, TimestampMixin):
    __tablename__ = "roles"
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)

    users: Mapped[List["User"]] = relationship("User", back_populates="role", lazy="selectin")

    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin"
    )
    def to_dict(self): return {"id": str(self.id), "name": self.name}


class Permission(Base, UUIDMixing, TimestampMixin):
    __tablename__ = "permissions"
    code: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="selectin"
    )
    def to_dict(self): return {"id": str(self.id), "code": self.code}


__all__ = ["Role", "Permission", "role_permissions"]
