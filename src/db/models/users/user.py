from datetime import datetime, date
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Integer, Date, DateTime

from db.base import Base, UUIDMixing, TimestampMixin, StatusMixin
from db.models.enums import UserStatus
from db.models.org.service import Service
from db.models.org.region import Region
from db.models.org.rank import Rank


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

    # relationships
    role: Mapped["Role"] = relationship("Role", back_populates="users", lazy="selectin")
    region: Mapped["Region"] = relationship("Region", lazy="selectin")
    service: Mapped["Service"] = relationship("Service", lazy="selectin")
    rank: Mapped["Rank"] = relationship("Rank", lazy="selectin")

    @property
    def full_name(self) -> str:
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

    def has_permission(self, code: str) -> bool:
        return code in self.permissions

    def change_status(self, new_status: str):
        if new_status not in [e.value for e in UserStatus]:
            raise ValueError("Invalid status")
        self.status = new_status

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE.value if self.status else False

    def soft_delete(self):
        self.status = UserStatus.BLOCKED.value

    @property
    def permissions(self) -> list[str]:
        if not self.role:
            return []
        return [p.code for p in self.role.permissions]

    __mapper_args__ = {"version_id_col": version}
