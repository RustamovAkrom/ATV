from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from db.base import Base, StatusMixin, TimestampMixin, UUIDMixing
from db.models.enums import UserStatus
from db.models.org.rank import Rank
from db.models.org.region import Region
from db.models.org.service import Service

if TYPE_CHECKING:
    from .permission import Role


class User(Base, UUIDMixing, TimestampMixin, StatusMixin):
    __tablename__ = "users"
    STATUS_ENUM = UserStatus

    login: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=UserStatus.ACTIVE.value, nullable=False)

    assigned_region_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("regions.id", ondelete="SET NULL"), nullable=True)
    assigned_service_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("services.id", ondelete="SET NULL"), nullable=True)
    rank_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("ranks.id", ondelete="SET NULL"), nullable=True)

    position: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    badge_number: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)
    passport_number: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)

    hired_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    dismissed_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_password_change: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    @validates
    def validate_status(self, value):
        return super().validate_status(value)

    role: Mapped["Role"] = relationship("Role", back_populates="users", lazy="selectin")
    region: Mapped["Region"] = relationship("Region", lazy="selectin")
    service: Mapped["Service"] = relationship("Service", lazy="selectin")
    rank: Mapped["Rank"] = relationship("Rank", lazy="selectin")

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE.value if self.status else False

    @property
    def permissions(self) -> list[str]:
        return [p.code for p in self.role.permissions] if self.role else []

    __mapper_args__ = {"version_id_col": version}
