from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.events.base import BaseEventService
from db.dependencies import get_db_session


def get_base_event_service() -> BaseEventService:
    return BaseEventService()
