from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, TimestampMixin, UUIDMixing

if TYPE_CHECKING:
    from .asset_model import AssetModel


class Manufacturer(Base, UUIDMixing, TimestampMixin):
    __tablename__ = "manufacturers"

    name: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    country: Mapped[str | None] = mapped_column(String(100))
    website: Mapped[str | None] = mapped_column(String(255))

    models: Mapped[List["AssetModel"]] = relationship(
        "AssetModel",
        back_populates="manufacturer",
        lazy="selectin"
    )
