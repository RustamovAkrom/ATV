# src/db/models/assets/asset.py

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID
from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy import Date, Enum as SAEnum, ForeignKey, Integer, Numeric, String, text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym, validates

from db.base import Base
from db.mixins import TimestampMixin, UUIDMixing, SlugMixin
from db.models.documents.document import Document
from db.models.enums import AssetStatus
from db.models.repairs.repair import Repair
from db.models.warehouse.warehouse import Warehouse

if TYPE_CHECKING:
    from db.models.assets.asset_assignment import AssetAssignment
    from db.models.assets.asset_class import AssetClass
    from db.models.assets.asset_history import AssetHistory
    from db.models.assets.asset_model import AssetModel
    from db.models.assets.asset_transfer import AssetTransfer
    from db.models.org.region import Region
    from db.models.org.service import Service
    from db.models.users.user import User


class Asset(Base, UUIDMixing, TimestampMixin, SlugMixin):
    __tablename__ = "assets"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    # type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Identifiers
    # asset_tag: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    serial_number: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True
    )

    # Relations (FK)
    model_id: Mapped[UUID] = mapped_column(
        ForeignKey("asset_models.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    status: Mapped[AssetStatus] = mapped_column(
        SAEnum(
            AssetStatus,
            name="asset_status",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=AssetStatus.ACTIVE,
        nullable=False,
    )

    class_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("asset_classes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    service_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("services.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    region_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("regions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    current_warehouse_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("warehouses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    owner_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # datesr
    commission_date: Mapped[date | None] = mapped_column(Date)
    warranty_end: Mapped[date | None] = mapped_column(Date)

    # State (0-100)
    condition_percent: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    # Finance
    purchase_date: Mapped[date | None] = mapped_column(Date)
    purchase_cost: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))

    # usage
    last_repair_date: Mapped[date | None] = mapped_column(Date)

    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    usage_intensity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # flags
    is_transfer_locked: Mapped[bool] = mapped_column(default=False, nullable=False)

    # flexible data
    meta: Mapped[dict] = mapped_column(
        "meta_data",
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb")
    )

    # relationships
    repairs: Mapped[list["Repair"]] = relationship(
        "Repair", back_populates="asset", lazy="selectin"
    )
    model: Mapped["AssetModel"] = relationship(
        "AssetModel", back_populates="assets", lazy="joined"
    )
    asset_class: Mapped[Optional["AssetClass"]] = relationship(
        "AssetClass", back_populates="assets", lazy="joined"
    )
    region: Mapped[Optional["Region"]] = relationship("Region", lazy="selectin")
    service: Mapped[Optional["Service"]] = relationship("Service", lazy="joined")

    warehouse: Mapped[Optional["Warehouse"]] = relationship(
        "Warehouse",
        back_populates="assets",
        lazy="selectin",
        foreign_keys=[current_warehouse_id],
    )
    owner: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[owner_id], lazy="selectin"
    )
    assignments: Mapped[list["AssetAssignment"]] = relationship(
        "AssetAssignment",
        back_populates="asset",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="AssetAssignment.assigned_at.desc()",
    )
    history_entries: Mapped[list["AssetHistory"]] = relationship(
        "AssetHistory",
        back_populates="asset",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="AssetHistory.created_at.desc()",
    )
    transfers: Mapped[list["AssetTransfer"]] = relationship(
        "AssetTransfer",
        back_populates="asset",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="AssetTransfer.transferred_at.desc()",
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="asset",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    responsible_user_id = synonym("owner_id")
    responsible_user = synonym("owner")

    @validates("condition_percent")
    def validate_condition(self, key, value):
        if not 0 <= value <= 100:
            raise ValueError("condition_percent must be between 0 and 100")
        return value

    @validates("status")
    def validate_status(self, key, value):
        if value == AssetStatus.ASSIGNED and self.owner_id is None:
            raise ValueError("ASSIGNED asset must have owner_id")
        if value == AssetStatus.ACTIVE and self.owner_id is not None:
            raise ValueError("ACTIVE asset cannot have owner_id")
        return value

    @hybrid_property
    def age_years(self) -> float | None:
        if self.commission_date:
            return (date.today() - self.commission_date).days / 365.25
        return None

    @property
    def is_under_warranty(self) -> bool:
        "Check warranty"
        return self.warranty_end and self.warranty_end >= date.today()

    __table_args__ = (
        Index('ix_assets_status_region', 'status', 'region_id'),
        Index('ix_assets_service_class', 'service_id', 'class_id'),
    )

    def __repr__(self):
        return self.name
