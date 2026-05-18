from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from db.mixins import TimestampMixin, UUIDMixing, SlugMixin

if TYPE_CHECKING:
    from db.models.org.service import Service
    from db.models.users.user import User


class Region(Base, UUIDMixing, TimestampMixin, SlugMixin):
    __tablename__ = "regions"
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("regions.id", ondelete="SET NULL")
    )

    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    geojson: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    children: Mapped[list["Region"]] = relationship(
        "Region", back_populates="parent", lazy="selectin"
    )
    parent: Mapped[Optional["Region"]] = relationship(
        "Region", remote_side="Region.id", back_populates="children", lazy="selectin"
    )
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="region", lazy="selectin"
    )

    services: Mapped[list["Service"]] = relationship(
        "Service",
        secondary="region_services",
        back_populates="regions",
        lazy="selectin",
    )
