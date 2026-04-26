from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from db.base import Base, StatusMixin, TimestampMixin, UUIDMixing
from db.models.assets.asset import Asset
from db.models.enums import UserStatus
from db.models.org.rank import Rank
from db.models.org.region import Region
from db.models.org.service import Service

if TYPE_CHECKING:
    from .permission import Role, Permission


class User(Base, UUIDMixing, TimestampMixin, StatusMixin):
    __tablename__ = "users"
    STATUS_ENUM = UserStatus

    login: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    role_id: Mapped[UUID] = mapped_column(
        ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50), default=UserStatus.ACTIVE.value, nullable=False
    )

    assigned_region_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("regions.id", ondelete="SET NULL"), nullable=True
    )
    assigned_service_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("services.id", ondelete="SET NULL"), nullable=True
    )
    rank_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("ranks.id", ondelete="SET NULL"), nullable=True
    )

    position: Mapped[str | None] = mapped_column(String(255), nullable=True)
    badge_number: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True
    )
    passport_number: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True
    )

    hired_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    dismissed_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_password_change: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    @validates
    def validate_status(self, value):
        return super().validate_status(value)

    role: Mapped["Role"] = relationship("Role", back_populates="users", lazy="selectin")
    region: Mapped["Region"] = relationship("Region", lazy="selectin")
    service: Mapped["Service"] = relationship("Service", lazy="selectin")
    rank: Mapped["Rank"] = relationship("Rank", lazy="selectin")
    owned_assets: Mapped[list["Asset"]] = relationship(
        "Asset",
        back_populates="owner",
        lazy="selectin",
        foreign_keys="Asset.owner_id",
    )
    # User-specific permissions (overrides)
    direct_permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary="user_permissions",
        back_populates="users",
        lazy="selectin",
    )

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE.value if self.status else False

    @hybrid_property
    def full_name(self) -> str:
        parts = [self.first_name, self.last_name]
        full_name = " ".join(part.strip() for part in parts if part and part.strip())
        return full_name or self.login

    @full_name.expression
    def full_name(cls):
        return func.trim(
            func.concat(
                func.coalesce(cls.first_name, ""),
                " ",
                func.coalesce(cls.last_name, ""),
            )
        )

    @property
    def permissions(self) -> list[str]:
        """
        Returns aggregated permissions from role and user-specific overrides.
        User permissions take precedence over role permissions.
        """
        perm_set = set()

        # Add role permissions
        if self.role and self.role.permissions:
            perm_set.update(p.code for p in self.role.permissions)

        # Add user-specific permissions (overrides)
        if self.direct_permissions:
            perm_set.update(p.code for p in self.direct_permissions)

        return list(perm_set)

    __mapper_args__ = {"version_id_col": version}
