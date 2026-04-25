from uuid import UUID

from core.exceptions.errors import NotFound, PermissionDenied
from repositories.session_repo import SessionRepository


class SessionService:
    def __init__(self, repo: SessionRepository):
        self.repo = repo

    async def list_user_sessions(self, user_id: UUID):
        sessions = await self.repo.get_user_sessions(user_id)
        return [self.repo._to_schema(s) for s in sessions]

    async def revoke_session(self, user_id: UUID, session_id: UUID):
        session = await self.repo.get_by_id(session_id)
        if not session:
            raise NotFound("Session not found")

        if session.user_id != user_id:
            raise PermissionDenied()

        if session.is_revoked:
            return  # indempotent

        await self.repo.revoke(session_id)

    async def revoke_all(self, user_id: UUID):
        await self.repo.revoke_all(user_id)

    async def cleanup_expired(self) -> int:
        return await self.repo.delete_expired_sessions()
