from datetime import datetime, date
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Boolean, Integer, Date, DateTime, Enum

from db.base import Base, UUIDMixing, TimestampMixin
from db.models.enums import UserStatus


if TYPE_CHECKING:
    from .role import Role


class User(Base, UUIDMixing, TimestampMixin):
    __tablename__ = "users"

    login: Mapped[str] = mapped_column(String(100), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))

    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))

    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True)

    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id"))
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus, name="user_status"), default=UserStatus.ACTIVE)

    # assigned_region_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("regions.id"))
    # assigned_service_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("services.id"))

    # rank_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("ranks.id"))

    position: Mapped[Optional[str]] = mapped_column(String(255))
    badge_number: Mapped[Optional[str]] = mapped_column(String(50))
    passport_number: Mapped[Optional[str]] = mapped_column(String(50))

    hired_at: Mapped[Optional[date]] = mapped_column(Date)
    dismissed_at: Mapped[Optional[date]] = mapped_column(Date)

    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_password_change: Mapped[Optional[datetime]] = mapped_column(DateTime)

    failed_login_attempts: Mapped[int] = mapped_column(default=0)
    is_two_factor_enabled: Mapped[bool] = mapped_column(default=False)

    version: Mapped[int] = mapped_column(default=1)

    # relationships
    role: Mapped["Role"] = relationship(lazy="selectin")

    # region = relationship("Region", lazy="selectin")
    # service = relationship("Service", lazy="selectin")

    @property
    def permissions(self) -> list[str]:
        if not self.role:
            return []
        return [p.code for p in self.role.permissions]
