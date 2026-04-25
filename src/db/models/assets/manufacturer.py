from typing import TYPE_CHECKING, List

from sqlalchemy import Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, TimestampMixin, UUIDMixing
from db.models.mixins.slug_mixin import SlugMixin

if TYPE_CHECKING:
    from .asset_model import AssetModel


class Manufacturer(Base, UUIDMixing, TimestampMixin, SlugMixin):
    __tablename__ = "manufacturers"

    name: Mapped[str] = mapped_column(String(150), index=True)
    code: Mapped[str] = mapped_column(String(150), unique=True)

    country: Mapped[str | None] = mapped_column(String(100))
    website: Mapped[str | None] = mapped_column(String(255))

    models: Mapped[List["AssetModel"]] = relationship(
        "AssetModel", back_populates="manufacturer", lazy="selectin"
    )

    __table_args__ = (
        Index("uq_manufacturer_name_lower", func.lower(name), unique=True),
    )
