from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text

from db.base import Base, UUIDMixing, TimestampMixin

if TYPE_CHECKING:
    from .asset import Asset


class AssetClass(Base, UUIDMixing, TimestampMixin):
    __tablename__ = "asset_classes"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    assets: Mapped[List["Asset"]] = relationship(
        "Asset",
        back_populates="asset_class",
        lazy="selectin"
    )

    # ======================
    # BUSINESS
    # ======================

    def is_it_related(self) -> bool:
        return self.code.startswith("IT")

    def is_transport(self) -> bool:
        return self.code.startswith("TR")
