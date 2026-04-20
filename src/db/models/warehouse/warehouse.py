# src/db/models/warehouse/warehouse.py

from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, TimestampMixin, UUIDMixing

if TYPE_CHECKING:
    from db.models.assets.asset import Asset
    from db.models.org.region import Region
    from db.models.org.service import Service
    from db.models.users.user import User


class Warehouse(Base, UUIDMixing, TimestampMixin):
    __tablename__ = "warehouses"

    # ======================
    # BASIC INFO
    # ======================

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(50), unique=True)

    # ======================
    # ORG STRUCTURE
    # ======================

    region_id: Mapped[UUID] = mapped_column(
        ForeignKey("regions.id", ondelete="RESTRICT"),
        nullable=False
    )
    service_id: Mapped[UUID] = mapped_column(
        ForeignKey("services.id", ondelete="SET NULL"),
        nullable=True,
    )
    manager_user_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)

    # ======================
    # FLAGS
    # ======================

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # ======================
    # RELATIONSHIPS
    # ======================

    assets: Mapped[List["Asset"]] = relationship(
        "Asset",
        back_populates="warehouse",
        lazy="selectin"
    )

    region: Mapped[Optional["Region"]] = relationship(
        "Region",
        lazy="selectin"
    )
    manager_user: Mapped[Optional["User"]] = relationship("User", lazy="selectin")
    service: Mapped[Optional["Service"]] = relationship("Service", lazy="selectin")
