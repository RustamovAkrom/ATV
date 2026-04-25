from typing import Optional

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base, TimestampMixin, UUIDMixin


class SystemConfig(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "system_configs"
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    value: Mapped[dict] = mapped_column(JSON)  # flexiable settings
    description: Mapped[Optional[str]] = mapped_column(Text)
