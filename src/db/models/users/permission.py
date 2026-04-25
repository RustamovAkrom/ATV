from typing import TYPE_CHECKING, List

from sqlalchemy import Column, ForeignKey, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, TimestampMixin, UUIDMixing

if TYPE_CHECKING:
    from .user import User

# MANY-TO-MANY TABLE
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Role(Base, UUIDMixing, TimestampMixin):
    __tablename__ = "roles"
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)

    users: Mapped[List["User"]] = relationship(
        "User", back_populates="role", lazy="selectin"
    )

    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin",
    )


class Permission(Base, UUIDMixing, TimestampMixin):
    __tablename__ = "permissions"
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    code: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="selectin",
    )


__all__ = ["Role", "Permission", "role_permissions"]
