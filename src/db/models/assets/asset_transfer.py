from datetime import datetime
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

    status: Mapped[TransferStatus] = mapped_column(
        SAEnum(
            TransferStatus,
            name="transferstatus",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=TransferStatus.PENDING,
        nullable=False,
    )
    from_warehouse_id: Mapped[UUID | None] = mapped_column(ForeignKey("warehouses.id"))
    to_warehouse_id: Mapped[UUID | None] = mapped_column(ForeignKey("warehouses.id"))

    from_service_id: Mapped[UUID | None] = mapped_column(ForeignKey("services.id"))
    to_service_id: Mapped[UUID | None] = mapped_column(ForeignKey("services.id"))

    transferred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    comment: Mapped[str | None] = mapped_column(String(255))

    # relationships
    asset = relationship("Asset", back_populates="transfers", lazy="selectin")
    from_warehouse = relationship(
        "Warehouse", foreign_keys=[from_warehouse_id], lazy="selectin"
    )
    to_warehouse = relationship(
        "Warehouse", foreign_keys=[to_warehouse_id], lazy="selectin"
    )
    from_service = relationship(
        "Service",
        foreign_keys=[from_service_id],
        lazy="selectin",
    )
    to_service = relationship(
        "Service",
        foreign_keys=[to_service_id],
        lazy="selectin",
    )

    received_by_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_by = relationship("User", foreign_keys=[created_by_id], lazy="selectin")
    received_by = relationship("User", foreign_keys=[received_by_id], lazy="selectin")
