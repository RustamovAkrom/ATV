from typing import Protocol
from uuid import UUID


class WSBackend(Protocol):
    async def publish(self, user_id: UUID, payload: dict) -> None: ...
