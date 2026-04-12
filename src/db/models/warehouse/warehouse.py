# src/db/models/warehouse/warehouse.py

from typing import List, Optional, TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Boolean

from db.base import Base, UUIDMixing, TimestampMixin

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
    manager_user_id: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id"))

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
    service: Mapped["Service"] = relationship(
        "Service",
        lazy="selectin"
    )

    # ======================
    # BUSINESS LOGIC
    # ======================

    def is_empty(self) -> bool:
        return len(self.assets) == 0

    def can_store_assets(self) -> bool:
        return self.is_active

    def deactivate(self):
        if not self.is_empty():
            raise ValueError("Cannot deactivate non-empty warehouse")

        self.is_active = False

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "code": self.code,
            "region_id": str(self.region_id),
            "service_id": str(self.service_id),
            "is_active": self.is_active,
        }
