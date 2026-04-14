from datetime import date
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from dateutil.relativedelta import relativedelta
from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from db.base import Base, TimestampMixin, UUIDMixing

if TYPE_CHECKING:
    from .asset import Asset
    from .asset_category import AssetCategory
    from .manufacturer import Manufacturer


class AssetModel(Base, UUIDMixing, TimestampMixin):
    __tablename__ = "asset_models"

    __table_args__ = (
        UniqueConstraint("name", "manufacturer_id", name="uq_model_manufacturer"),
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)

    manufacturer_id: Mapped[UUID] = mapped_column(
        ForeignKey("manufacturers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    category_id: Mapped[UUID] = mapped_column(
        ForeignKey("asset_categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    lifetime_years: Mapped[Optional[int]] = mapped_column(Integer)
    warranty_months: Mapped[Optional[int]] = mapped_column(Integer)

    # RELATIONSHIPS
    manufacturer: Mapped["Manufacturer"] = relationship(
        "Manufacturer",
        back_populates="models",
        lazy="selectin"
    )

    category: Mapped["AssetCategory"] = relationship(
        "AssetCategory",
        back_populates="models",
        lazy="selectin"
    )

    assets: Mapped[List["Asset"]] = relationship(
        "Asset",
        back_populates="model",
        lazy="selectin"
    )

    # ======================
    # VALIDATION
    # ======================

    @validates("lifetime_years")
    def validate_lifetime(self, key, value):
        if value is not None and value < 0:
            raise ValueError("lifetime_years must be >= 0")
        return value

    @validates("warranty_months")
    def validate_warranty(self, key, value):
        if value is not None and value < 0:
            raise ValueError("warranty_months must be >= 0")
        return value

    # ======================
    # BUSINESS LOGIC
    # ======================

    def get_warranty_end(self, purchase_date: date | None) -> Optional[date]:
        """
        Рассчитать дату окончания гарантии
        """
        if not purchase_date or not self.warranty_months:
            return None

        return purchase_date + relativedelta(months=self.warranty_months)

    def get_lifecycle_stage(self, purchase_date: date | None) -> str:
        """
        Определить стадию жизненного цикла
        """
        if not purchase_date or not self.lifetime_years:
            return "unknown"

        age = date.today().year - purchase_date.year

        if age < self.lifetime_years * 0.5:
            return "new"
        elif age < self.lifetime_years:
            return "normal"
        elif age < self.lifetime_years * 1.5:
            return "old"
        return "critical"

    def is_out_of_warranty(self, purchase_date: date | None) -> bool:
        """
        Проверка гарантии
        """
        end_date = self.get_warranty_end(purchase_date)
        if not end_date:
            return False
        return date.today() > end_date

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "manufacturer_id": str(self.manufacturer_id),
            "category_id": str(self.category_id),
            "lifetime_years": self.lifetime_years,
            "warranty_months": self.warranty_months,
        }
