# src/db/models/repairs/repair_part.py

from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from db.base import Base, UUIDMixing

if TYPE_CHECKING:
    pass


class RepairPart(Base, UUIDMixing):
    __tablename__ = "repair_parts"

    repair_id: Mapped[UUID] = mapped_column(
        ForeignKey("repairs.id", ondelete="CASCADE"),
        index=True,
    )
    part_name: Mapped[str] = mapped_column(String(150), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=False
    )

    repair = relationship("Repair", back_populates="parts", lazy="selectin")

    @validates("quantity")
    def validate_quantity(self, key, value):
        if value <= 0:
            raise ValueError("quantity must be > 0")
        return value
