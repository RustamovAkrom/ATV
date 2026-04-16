from uuid import UUID

from core.exceptions.errors import InvalidToken, NotFound, PermissionDenied
from repositories.session_repo import SessionRepository


class SessionService:
    def __init__(self, repo: SessionRepository):
        self.repo = repo

    async def list_user_sessions(self, user_id: UUID):
        return await self.repo.get_user_sessions(user_id)

    async def revoke_session(self, user_id: UUID, session_id: UUID):
        session = await self.repo.get_by_id(session_id)

        if not session:
            raise NotFound("Session not found")

        if session.user_id != user_id:
            raise PermissionDenied()

        if session.is_revoked:
            return # indempotent

        await self.repo.revoke(session_id)

    async def revoke_all(self, user_id: UUID):
        await self.repo.revoke_all(user_id)
