from __future__ import annotations

from datetime import date, datetime, time

from sqlalchemy import func, select

from db.models.approvals.approval_request import ApprovalRequest
from db.models.enums import ApprovalStatus
from repositories.base import BaseRepository


class ApprovalAnalyticsRepository(BaseRepository):
    @staticmethod
    def _date_filters(date_from: date | None, date_to: date | None):
        filters = []
        if date_from:
            filters.append(ApprovalRequest.created_at >= datetime.combine(date_from, time.min))
        if date_to:
            filters.append(ApprovalRequest.created_at <= datetime.combine(date_to, time.max))
        return filters

    async def metrics(self, date_from: date | None, date_to: date | None):
        dfilters = self._date_filters(date_from, date_to)
        return (
            await self.execute(
                select(
                    func.count(ApprovalRequest.id)
                    .filter(ApprovalRequest.status == ApprovalStatus.PENDING)
                    .label("pending_approvals"),
                    func.count(ApprovalRequest.id)
                    .filter(ApprovalRequest.status == ApprovalStatus.REJECTED)
                    .label("rejected_count"),
                    func.count(ApprovalRequest.id)
                    .filter(
                        ApprovalRequest.status.in_(
                            [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED]
                        )
                    )
                    .label("decided_count"),
                    func.avg(
                        func.extract(
                            "epoch", ApprovalRequest.decided_at - ApprovalRequest.created_at
                        )
                        / 3600.0
                    )
                    .filter(ApprovalRequest.decided_at.isnot(None))
                    .label("avg_approval_hours"),
                ).where(*dfilters)
            )
        ).one()
