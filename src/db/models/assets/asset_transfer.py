from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from db.base import Base, TimestampMixin, UUIDMixing
from db.models.enums import TransferStatus


class AssetTransfer(Base, UUIDMixing, TimestampMixin):
    __tablename__ = "asset_transfers"

    asset_id: Mapped[UUID] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"),
        index=True,
    )
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    status: Mapped[TransferStatus] = mapped_column(SAEnum(TransferStatus), default=TransferStatus.PENDING.value)
    from_warehouse_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("warehouses.id"))
    to_warehouse_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("warehouses.id"))

    from_service_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("services.id"))
    to_service_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("services.id"))

    transferred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    comment: Mapped[Optional[str]] = mapped_column(String(255))

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

    received_by_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
