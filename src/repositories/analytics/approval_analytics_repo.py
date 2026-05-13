from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import func, select

from db.models.approvals.approval_request import ApprovalRequest
from db.models.enums import ApprovalStatus
from repositories.analytics.base_analytics_repo import BaseAnalyticsRepository


class ApprovalAnalyticsRepository(BaseAnalyticsRepository):
    """Репозиторий для аналитики согласований"""

    async def metrics(
        self,
        date_from: date | None = None,
        date_to: date | None = None
    ) -> dict:
        """Метрики по согласованиям"""
        filters = self.date_filters(ApprovalRequest.created_at, date_from, date_to)

        query = select(
            func.count(ApprovalRequest.id)
            .filter(ApprovalRequest.status == ApprovalStatus.PENDING)
            .label("pending_approvals"),
            func.count(ApprovalRequest.id)
            .filter(ApprovalRequest.status == ApprovalStatus.REJECTED)
            .label("rejected_count"),
            func.count(ApprovalRequest.id)
            .filter(ApprovalRequest.status.in_([ApprovalStatus.APPROVED, ApprovalStatus.REJECTED]))
            .label("decided_count"),
            func.avg(
                func.extract("epoch", ApprovalRequest.decided_at - ApprovalRequest.created_at) / 3600.0
            )
            .filter(ApprovalRequest.decided_at.isnot(None))
            .label("avg_approval_hours"),
        ).where(*filters)

        result = await self.session.execute(query)
        row = result.one()

        return {
            "pending_approvals": row.pending_approvals or 0,
            "rejected_count": row.rejected_count or 0,
            "decided_count": row.decided_count or 0,
            "avg_approval_hours": float(row.avg_approval_hours) if row.avg_approval_hours else 0,
        }
