# src/db/models/repairs/repair.py

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.sql import func

from db.base import Base, TimestampMixin, UUIDMixing
from db.models.enums import RepairStatus

if TYPE_CHECKING:
    from .repair_part import RepairPart


class Repair(Base, UUIDMixing, TimestampMixin):
    __tablename__ = "repairs"

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

    description: Mapped[Optional[str]] = mapped_column(String(500))

    status: Mapped[RepairStatus] = mapped_column(
        SAEnum(RepairStatus),
        default=RepairStatus.REPORTED,
        nullable=False
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    labor_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))

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

    @validates("labor_cost", "total_cost")
    def validate_costs(self, key, value):
        if value is not None and value < 0:
            raise ValueError(f"{key} must be >= 0")
        return value
