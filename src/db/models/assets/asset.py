# src/db/models/assets/asset.py

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import JSON, CheckConstraint, Date
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from db.base import Base, TimestampMixin, UUIDMixing
from db.models.enums import AssetStatus, LifecycleStage

if TYPE_CHECKING:
    from db.models.assets.asset_class import AssetClass
    from db.models.assets.asset_model import AssetModel
    from db.models.documents.document import Document
    from db.models.org.region import Region
    from db.models.org.service import Service
    from db.models.repairs.repair import Repair
    from db.models.users.user import User
    from db.models.warehouse.warehouse import Warehouse


class Asset(Base, UUIDMixing, TimestampMixin):
    __tablename__ = "assets"

    # Identifiers
    asset_tag: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)

    # Relations (FK)
    model_id: Mapped[UUID] = mapped_column(
        ForeignKey("asset_models.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    status: Mapped[AssetStatus] = mapped_column(
        SAEnum(AssetStatus, name="asset_status"), default=AssetStatus.IN_STOCK, nullable=False
    )

    class_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("asset_classes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    service_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("services.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    region_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("regions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    current_warehouse_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("warehouses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    responsible_user_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # dates
    commission_date: Mapped[Optional[date]] = mapped_column(Date)
    warranty_end: Mapped[Optional[date]] = mapped_column(Date)


    # State (0-100)
    condition_percent: Mapped[int] = mapped_column(default=100)

    # Finance
    purchase_date: Mapped[Optional[date]] = mapped_column(Date)
    purchase_cost: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2)
    )

    # usage
    last_repair_date: Mapped[Optional[date]] = mapped_column(Date)
    failure_count: Mapped[int] = mapped_column(default=0)
    usage_intensity: Mapped[int] = mapped_column(default=0)

    # flags
    is_transfer_locked: Mapped[bool] = mapped_column(default=False)

    # flexible data
    meta: Mapped[dict] = mapped_column("metadata", JSON, default=lambda: {}, nullable=False)

    # versioning
    version: Mapped[int] = mapped_column(Integer, default=1)

    # relationships
    repairs: Mapped[list["Repair"]] = relationship(
        "Repair",
        back_populates="asset",
        lazy="selectin"
    )
    model: Mapped["AssetModel"] = relationship("AssetModel", back_populates="assets", lazy="joined")
    asset_class: Mapped[Optional["AssetClass"]] = relationship("AssetClass", back_populates="assets", lazy="joined")
    region: Mapped[Optional["Region"]] = relationship("Region", lazy="selectin")
    service: Mapped[Optional["Service"]] = relationship("Service", lazy="joined")
    warehouse: Mapped[Optional["Warehouse"]] = relationship(
        "Warehouse",
        back_populates="assets",
        lazy="selectin",
        foreign_keys=[current_warehouse_id],
    )
    responsible_user: Mapped[Optional["User"]] = relationship("User", lazy="selectin")
    documents: Mapped[List["Document"]] = relationship(
        "Document",
        back_populates="asset",
        lazy="selectin",
        cascade="all, delete-orphan"
    )

    @validates("condition_percent")
    def validate_condition(self, key, value):
        if not 0 <= value <= 100:
            raise ValueError("condition_percent must be between 0 and 100")
        return value

    __mapper_args__ = {
        "version_id_col": version
    }
