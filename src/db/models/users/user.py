from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from db.base import Base
from db.mixins import StatusMixin, TimestampMixin, UUIDMixing
from db.models.assets.asset import Asset
from db.models.enums import (
    EmploymentType,
    UserGender,
    UserLanguage,
    UserStatus,
)
from db.models.org.region import Region
from db.models.org.service import Service

if TYPE_CHECKING:
    from db.models.org.department import Department

    from .permission import Permission, Role


class User(Base, UUIDMixing, TimestampMixin, StatusMixin):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_region_service", "assigned_region_id", "assigned_service_id"),
        Index("ix_users_status_role", "status", "role_id"),
        Index("ix_users_hired_status", "hired_at", "status"),
    )
    STATUS_ENUM = UserStatus

    # ========== БАЗОВЫЕ ПОЛЯ ==========
    login: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    # ========== РОЛИ И СТАТУСЫ ==========
    role_id: Mapped[UUID] = mapped_column(
        ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[UserStatus] = mapped_column(
        SAEnum(
            UserStatus,
            name="user_status",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        default=UserStatus.ACTIVE,
        nullable=False,
    )

    # ========== ORGANIZATIONAL STRUCTURE ==========
    assigned_region_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("regions.id", ondelete="SET NULL"), nullable=True
    )
    assigned_service_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("services.id", ondelete="SET NULL"), nullable=True
    )
    department_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )

    # ========== РАБОЧАЯ ИНФОРМАЦИЯ ==========
    position: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="Department/division"
    )
    employment_type: Mapped[EmploymentType | None] = mapped_column(
        SAEnum(EmploymentType, name="employment_type"),
        nullable=True,
        comment="Type of employment",
    )

    # ========== ПЕРСОНАЛЬНЫЕ ДАННЫЕ ==========
    date_of_birth: Mapped[date | None] = mapped_column(
        Date, nullable=True, comment="Date of birth"
    )
    gender: Mapped[UserGender | None] = mapped_column(
        SAEnum(UserGender, name="gender"), nullable=True, comment="Gender"
    )

    # ========== ДОКУМЕНТЫ ==========
    badge_number: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True, comment="Employee badge number"
    )
    passport_number: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True, comment="Passport number"
    )

    # ========== ДАТЫ ТРУДОУСТРОЙСТВА ==========
    hired_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    dismissed_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    # ========== АВАТАРЫ ==========
    avatar_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="URL user avatar"
    )

    # ========== НАСТРОЙКИ ==========
    language: Mapped[UserLanguage] = mapped_column(
        SAEnum(UserLanguage, name="user_language"),
        default=UserLanguage.RU,  # <-- ИСПРАВЛЕНО: RU вместо EN для госсистемы
        nullable=False,
        comment="Interface language",
    )
    timezone: Mapped[str | None] = mapped_column(
        String(50), nullable=True, default="Asia/Tashkent", comment="Timezone (IANA)"
    )

    # ========== ВРЕМЕННЫЕ МЕТКИ ==========
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_password_change: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    @validates("badge_number")
    def validate_badge_number(self, key, value):
        if value and len(value) > 50:
            raise ValueError("Badge number too long (max 50 chars)")
        return value

    @validates("passport_number")
    def validate_passport_number(self, key, value):
        if value and len(value) > 50:
            raise ValueError("Passport number too long (max 50 chars)")
        return value

    @validates("timezone")
    def validate_timezone(self, key, value):
        if value:
            import zoneinfo

            try:
                zoneinfo.ZoneInfo(value)
            except zoneinfo.ZoneInfoNotFoundError as e:
                raise ValueError(f"Invalid timezone: {value}") from e
        return value

    # ========== RELATIONSHIPS ==========
    role: Mapped["Role"] = relationship("Role", back_populates="users", lazy="selectin")
    region: Mapped["Region"] = relationship("Region", lazy="selectin")
    service: Mapped["Service"] = relationship("Service", lazy="selectin")
    assigned_department: Mapped["Department"] = relationship(
        "Department", lazy="selectin"
    )
    owned_assets: Mapped[list["Asset"]] = relationship(
        "Asset",
        back_populates="owner",
        lazy="selectin",
        foreign_keys="Asset.owner_id",
    )
    direct_permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary="user_permissions",
        back_populates="users",
        lazy="selectin",
    )

    # ========== СВОЙСТВА ==========
    @property
    def is_active(self) -> bool:
        if not self.status:
            return False
        # status is a SQLAlchemy Enum mapped to UserStatus — compare as enum, not string
        return self.status == UserStatus.ACTIVE

    @hybrid_property
    def full_name(self) -> str:  # pyright: ignore[reportRedeclaration]
        """Полное имя: Имя Фамилия"""
        parts = [self.first_name, self.last_name]
        full_name = " ".join(part.strip() for part in parts if part and part.strip())
        return full_name or self.login

    @full_name.expression
    def full_name(cls):
        return func.coalesce(
            func.nullif(
                func.trim(
                    func.coalesce(cls.first_name, "")
                    + " "
                    + func.coalesce(cls.last_name, "")
                ),
                "",
            ),
            cls.login,
        )

    @property
    def short_name(self) -> str:
        """Короткое имя: Фамилия И."""
        result = self.last_name or ""
        if self.first_name:
            result += f" {self.first_name[0]}."
        return result or self.login

    @property
    def permissions(self) -> list[str]:
        """Агрегированные права пользователя (роль + персональные)"""
        perm_set = set()

        if self.role and self.role.permissions:
            perm_set.update(p.slug for p in self.role.permissions)

        if self.direct_permissions:
            perm_set.update(p.slug for p in self.direct_permissions)

        return list(perm_set)

    @property
    def is_employed(self) -> bool:
        return (
            self.hired_at
            and self.hired_at <= date.today()
            and (not self.dismissed_at or self.dismissed_at > date.today())
        ) or False

    def __repr__(self):
        return self.login
