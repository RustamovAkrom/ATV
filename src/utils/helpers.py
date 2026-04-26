import hashlib
from datetime import UTC, datetime

from fastapi import Request


def utc_now() -> datetime:
    return datetime.now(UTC)


def generate_device_id(request: Request) -> str:
    user_agent = request.headers.get("user-agent", "")
    ip = request.client.host if request.client else ""
    raw = f"{user_agent}:{ip}"
    return hashlib.sha256(raw.encode()).hexdigest()
