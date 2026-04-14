# src/db/models/audit_log.py

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base, UUIDMixing


class AuditLog(Base, UUIDMixing):
    __tablename__ = "audit_logs"

    method: Mapped[str] = mapped_column(String(10))
    path: Mapped[str] = mapped_column(String(255), index=True)

    status_code: Mapped[int] = mapped_column(Integer)

    user_id: Mapped[Optional[str]] = mapped_column(String(36), index=True)

    request_id: Mapped[str] = mapped_column(String(36), index=True)

    latency_ms: Mapped[int] = mapped_column(Integer)

    ip: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    query: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_suspicious: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
