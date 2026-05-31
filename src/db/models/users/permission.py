from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from db.mixins import SlugMixin, TimestampMixin, UUIDMixing

if TYPE_CHECKING:
    from .user import User

# MANY-TO-MANY: Role ↔ Permission
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

# MANY-TO-MANY: User ↔ Permission (for user-specific overrides)
user_permissions = Table(
    "user_permissions",
    Base.metadata,
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Role(Base, UUIDMixing, TimestampMixin, SlugMixin):
    __tablename__ = "roles"
    __role_permissions_table__ = "role_permissions"

    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)

    users: Mapped[list["User"]] = relationship(
        "User", back_populates="role", lazy="selectin"
    )

    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin",
    )

    def __repr__(self):
        return self.name


class Permission(Base, UUIDMixing, TimestampMixin, SlugMixin):
    __tablename__ = "permissions"
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)

    # Relations
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="selectin",
    )
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="user_permissions",
        back_populates="direct_permissions",
        lazy="selectin",
    )

    def __repr__(self):
        return self.name


__all__ = ["Permission", "Role", "role_permissions", "user_permissions"]
