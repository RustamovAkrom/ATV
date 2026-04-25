from schemas.analytics.dashboard.services import ServiceBreakdownOut
from repositories.analytics.dashboard.service_repo import ServiceAnalyticsRepository

class ServiceAnalyticsService:
    def __init__(self, repo: ServiceAnalyticsRepository):
        self.repo = repo

    async def get_breakdown(self):
        rows = await self.repo.get_service_stats()

        return [
            ServiceBreakdownOut(
                service_id=r.id,
                service_name=r.name,
                total_assets=r.total or 0,
                active_assets=r.active or 0,
                in_repair=r.repair or 0,
            )
            for r in rows
        ]
