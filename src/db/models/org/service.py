from typing import Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Table, Column, UUID, ForeignKey
from db.base import Base, UUIDMixing, TimestampMixin

if TYPE_CHECKING:
    from db.models.users.user import User
    from .region import Region


class Service(Base, UUIDMixing, TimestampMixin):
    __tablename__ = "services"
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    code: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)

    regions: Mapped[list["Region"]] = relationship(
        "Region",
        secondary="region_services",
        back_populates="services",
        lazy="selectin"
    )
    users: Mapped[list["User"]] = relationship("User", back_populates="service", lazy="selectin")


region_services = Table(
    "region_services", Base.metadata,
    Column("region_id", UUID(as_uuid=True), ForeignKey("regions.id", ondelete="CASCADE"), primary_key=True),
    Column("service_id", UUID(as_uuid=True), ForeignKey("services.id", ondelete="CASCADE"), primary_key=True),
)
