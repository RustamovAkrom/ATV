from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, Boolean, Column, Float, ForeignKey, String, Table, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from db.mixins import SlugMixin, TimestampMixin, UUIDMixing

if TYPE_CHECKING:
    from db.models.org.region import Region
    from db.models.org.service import Service


department_services = Table(
    "department_services",
    Base.metadata,
    Column(
        "department_id",
        PGUUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "service_id",
        PGUUID(as_uuid=True),
        ForeignKey("services.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Department(Base, UUIDMixing, TimestampMixin, SlugMixin):
    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)

    region_id: Mapped[UUID] = mapped_column(
        ForeignKey("regions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    meta: Mapped[dict | None] = mapped_column("meta_data", JSON, nullable=True)

    region: Mapped["Region"] = relationship(
        "Region", back_populates="departments", lazy="joined"
    )
    parent: Mapped["Department | None"] = relationship(
        "Department",
        remote_side="Department.id",
        back_populates="children",
        lazy="selectin",
    )
    children: Mapped[list["Department"]] = relationship(
        "Department", back_populates="parent", lazy="selectin"
    )
    services: Mapped[list["Service"]] = relationship(
        "Service",
        secondary=department_services,
        back_populates="departments",
        lazy="selectin",
    )

    def __repr__(self):
        return self.name
