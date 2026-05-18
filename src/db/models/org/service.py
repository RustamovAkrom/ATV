from typing import TYPE_CHECKING

from sqlalchemy import UUID, Column, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from db.mixins import TimestampMixin, UUIDMixing, SlugMixin

if TYPE_CHECKING:
    from db.models.users.user import User

    from .region import Region


class Service(Base, UUIDMixing, TimestampMixin, SlugMixin):
    __tablename__ = "services"
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)

    regions: Mapped[list["Region"]] = relationship(
        "Region",
        secondary="region_services",
        back_populates="services",
        lazy="selectin",
    )
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="service", lazy="selectin"
    )


region_services = Table(
    "region_services",
    Base.metadata,
    Column(
        "region_id",
        UUID(as_uuid=True),
        ForeignKey("regions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "service_id",
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
