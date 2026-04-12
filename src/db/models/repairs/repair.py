# src/db/models/repairs/repair.py

from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy import (
    String,
    ForeignKey,
    DateTime,
    Numeric,
    Enum as SAEnum,
)

from db.base import Base, UUIDMixing, TimestampMixin
from db.models.enums import RepairStatus

if TYPE_CHECKING:
    from db.models.assets.asset import Asset
    from db.models.users.user import User
    from .repair_part import RepairPart


class Repair(Base, UUIDMixing, TimestampMixin):
    __tablename__ = "repairs"

    # ======================
    # FK
    # ======================

    asset_id: Mapped[UUID] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    reported_by_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id"),
        index=True,
    )

    assigned_to_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id"),
        index=True,
    )

    # ======================
    # DATA
    # ======================

    description: Mapped[Optional[str]] = mapped_column(String(500))

    status: Mapped[RepairStatus] = mapped_column(
        SAEnum(RepairStatus),
        default=RepairStatus.REPORTED,
        nullable=False
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    labor_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    total_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))

    # ======================
    # RELATIONSHIPS
    # ======================

    asset = relationship("Asset", back_populates="repairs", lazy="selectin")

    reported_by = relationship(
        "User",
        foreign_keys=[reported_by_id],
        lazy="selectin"
    )

    assigned_to = relationship(
        "User",
        foreign_keys=[assigned_to_id],
        lazy="selectin"
    )

    parts: Mapped[List["RepairPart"]] = relationship(
        "RepairPart",
        back_populates="repair",
        lazy="selectin"
    )

    # ======================
    # VALIDATION
    # ======================

    @validates("labor_cost", "total_cost")
    def validate_costs(self, key, value):
        if value is not None and value < 0:
            raise ValueError(f"{key} must be >= 0")
        return value

    # ======================
    # BUSINESS LOGIC
    # ======================

    def start(self):
        if self.status != RepairStatus.REPORTED:
            raise ValueError("Repair already started or invalid state")

        self.status = RepairStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()

    def complete(self):
        if self.status != RepairStatus.IN_PROGRESS:
            raise ValueError("Repair not in progress")

        self.status = RepairStatus.DONE
        self.completed_at = datetime.utcnow()

    def cancel(self):
        if self.status == RepairStatus.DONE:
            raise ValueError("Cannot cancel completed repair")

        self.status = RepairStatus.CANCELED

    def calculate_total_cost(self):
        parts_cost = sum(p.total_price for p in self.parts if p.total_price)
        self.total_cost = (self.labor_cost or 0) + parts_cost
