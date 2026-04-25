from collections.abc import Mapping
from typing import Any
from uuid import UUID

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.audit.audit_log import AuditLog
from schemas.audit import AuditCreateSchema, AuditFiltersSchema


class AuditRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _normalize_payload(
        data: AuditCreateSchema | Mapping[str, Any],
    ) -> dict[str, Any]:
        if hasattr(data, "model_dump"):
            return data.model_dump()
        if isinstance(data, Mapping):
            return dict(data)
        raise TypeError("AuditRepository.create expects AuditCreate or mapping")

    @staticmethod
    def _base_query():
        return select(AuditLog)

    @staticmethod
    def _count_query(query):
        return select(func.count()).select_from(query.order_by(None).subquery())

    @staticmethod
    def _apply_filters(query, filters: AuditFiltersSchema | None):
        if filters is None:
            return query

        conditions = []

        if filters.user_id is not None:
            conditions.append(AuditLog.user_id == str(filters.user_id))

        if filters.request_id:
            conditions.append(AuditLog.request_id == filters.request_id)

        if filters.method:
            conditions.append(AuditLog.method == str(filters.method))

        if filters.status_code is not None:
            conditions.append(AuditLog.status_code == filters.status_code)

        if filters.status_min is not None:
            conditions.append(AuditLog.status_code >= filters.status_min)

        if filters.status_max is not None:
            conditions.append(AuditLog.status_code <= filters.status_max)

        if filters.from_date is not None:
            conditions.append(AuditLog.created_at >= filters.from_date)

        if filters.to_date is not None:
            conditions.append(AuditLog.created_at <= filters.to_date)

        if filters.is_suspicious is not None:
            conditions.append(AuditLog.is_suspicious.is_(filters.is_suspicious))

        if filters.search:
            term = f"%{filters.search}%"
            conditions.append(
                or_(
                    AuditLog.path.ilike(term),
                    AuditLog.request_id.ilike(term),
                    AuditLog.method.ilike(term),
                    AuditLog.ip.ilike(term),
                    AuditLog.user_agent.ilike(term),
                    AuditLog.query.ilike(term),
                )
            )

        if conditions:
            query = query.where(and_(*conditions))

        return query

    async def create(self, data: AuditCreateSchema | Mapping[str, Any]):
        payload = self._normalize_payload(data)
        audit = AuditLog(**payload)
        self.session.add(audit)
        await self.session.flush()
        return audit

    async def list(self, filters: AuditFiltersSchema | None, limit: int, offset: int):
        query = self._apply_filters(self._base_query(), filters).order_by(
            AuditLog.created_at.desc()
        )
        result = await self.session.execute(query.limit(limit).offset(offset))
        items = result.scalars().all()

        total = await self.session.scalar(self._count_query(query))
        return items, int(total or 0)

    async def get_recent(self, limit: int, offset: int):
        query = self._base_query().order_by(AuditLog.created_at.desc())

        result = await self.session.execute(query.limit(limit).offset(offset))
        items = result.scalars().all()

        total = await self.session.scalar(select(func.count()).select_from(AuditLog))
        return items, int(total or 0)

    async def get_by_request_id(self, request_id: str, limit: int, offset: int):
        query = (
            self._base_query()
            .where(AuditLog.request_id == request_id)
            .order_by(AuditLog.created_at.asc())
        )

        result = await self.session.execute(query.limit(limit).offset(offset))
        items = result.scalars().all()

        total = await self.session.scalar(
            select(func.count()).select_from(
                select(AuditLog).where(AuditLog.request_id == request_id).subquery()
            )
        )
        return items, int(total or 0)

    async def get_by_user(self, user_id: UUID, limit: int, offset: int):
        query = (
            self._base_query()
            .where(AuditLog.user_id == str(user_id))
            .order_by(AuditLog.created_at.desc())
        )

        result = await self.session.execute(query.limit(limit).offset(offset))
        items = result.scalars().all()

        total = await self.session.scalar(
            select(func.count()).select_from(
                select(AuditLog).where(AuditLog.user_id == str(user_id)).subquery()
            )
        )
        return items, int(total or 0)

    async def get_by_status_code(self, status_code: int, limit: int, offset: int):
        query = (
            self._base_query()
            .where(AuditLog.status_code == status_code)
            .order_by(AuditLog.created_at.desc())
        )

        result = await self.session.execute(query.limit(limit).offset(offset))
        items = result.scalars().all()

        total = await self.session.scalar(
            select(func.count()).select_from(
                select(AuditLog).where(AuditLog.status_code == status_code).subquery()
            )
        )
        return items, int(total or 0)

    async def get_errors(self, limit: int, offset: int):
        query = (
            self._base_query()
            .where(AuditLog.status_code >= 400)
            .order_by(AuditLog.created_at.desc())
        )

        result = await self.session.execute(query.limit(limit).offset(offset))
        items = result.scalars().all()

        total = await self.session.scalar(
            select(func.count()).select_from(
                select(AuditLog).where(AuditLog.status_code >= 400).subquery()
            )
        )
        return items, int(total or 0)

    async def get_stats(self):
        result = await self.session.execute(
            select(
                func.count().label("total"),
                func.count().filter(AuditLog.status_code >= 400).label("errors"),
                func.count().filter(AuditLog.status_code >= 500).label("server_errors"),
                func.count()
                .filter(AuditLog.is_suspicious.is_(True))
                .label("suspicious"),
                func.count(func.distinct(AuditLog.user_id)).label("unique_users"),
            )
        )

        row = result.one()

        return {
            "total": int(row.total or 0),
            "errors": int(row.errors or 0),
            "server_errors": int(row.server_errors or 0),
            "suspicious": int(row.suspicious or 0),
            "unique_users": int(row.unique_users or 0),
        }
