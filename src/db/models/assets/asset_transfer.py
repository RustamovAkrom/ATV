from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, String

from db.base import Base, UUIDMixing, TimestampMixin

if TYPE_CHECKING:
    from .asset import Asset


class AssetTransfer(Base, UUIDMixing, TimestampMixin):
    __tablename__ = "asset_transfers"

    asset_id: Mapped[UUID] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"),
        index=True,
    )

    from_warehouse_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("warehouses.id")
    )

    to_warehouse_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("warehouses.id")
    )

    from_service_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("services.id")
    )

    to_service_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("services.id")
    )

    transferred_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    comment: Mapped[Optional[str]] = mapped_column(String(255))

    # relationships
    asset = relationship("Asset", lazy="selectin")
    from_warehouse = relationship(
        "Warehouse",
        foreign_keys=[from_warehouse_id],
        lazy="selectin"
    )
    to_warehouse = relationship(
        "Warehouse",
        foreign_keys=[to_warehouse_id],
        lazy="selectin"
    )

    # business
    def is_internal_transfer(self) -> bool:
        return self.from_service_id == self.to_service_id

    def is_warehouse_transfer(self) -> bool:
        return self.from_warehouse_id != self.to_warehouse_id
