"""Expenses module - tracks all financial transactions."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from db.base import Base
from db.mixins import TimestampMixin, UUIDMixing
from db.models.enums import ExpenseTypeEnum


class Expense(Base, UUIDMixing, TimestampMixin):
    """Model for tracking expenses related to assets, repairs, and operations."""

    __tablename__ = "expenses"

    # Foreign keys
    asset_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("assets.id", ondelete="SET NULL"), nullable=True, index=True
    )
    repair_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("repairs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    region_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("regions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    service_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("services.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Core fields
    expense_type_code: Mapped[ExpenseTypeEnum] = mapped_column(
        Enum(ExpenseTypeEnum), nullable=False, index=True
    )  # purchase, repair, maintenance, logistics, other
    amount: Mapped[float] = mapped_column(
        Numeric(18, 2), nullable=False
    )  # Must be positive
    currency: Mapped[str] = mapped_column(String(10), default="UZS")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    # Timestamps
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_expense_amount_positive"),
        Index("ix_expenses_asset_region", "asset_id", "region_id"),
        Index("ix_expenses_type_date", "expense_type_code", "occurred_at"),
        Index("ix_expenses_created_occurred", "created_at", "occurred_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<Expense {self.id}: {self.amount} "
            f"{self.currency} ({self.expense_type_code})>"
        )

    # @hybrid_property
    # def amount_usd(self) -> float | None:
    #     if self.currency == "UZS":
    #         return self.amount / 13000  # пример курса
    #     return self.amount

    @hybrid_property
    def amount_formatted(self) -> str:
        """Formatted amount with currency."""
        return f"{self.amount:,.2f} {self.currency}"

    @hybrid_property
    def amount_usd(self) -> float | None:
        """Конвертация в USD."""
        if self.currency == "UZS":
            return self.amount / 13000  # TODO: Change automaticaly dependens on UZS
        return self.amount
