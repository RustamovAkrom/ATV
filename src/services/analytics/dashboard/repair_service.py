from schemas.analytics.dashboard.repairs import RepairOut, RepairSummaryOut


class RepairAnalyticsService:
    def __init__(self, repo):
        self.repo = repo

    async def get_recent(self):
        repairs = await self.repo.get_recent_repairs()

        return [
            RepairOut(
                id=r.id,
                asset_id=r.asset_id,
                asset_name=r.asset.name if r.asset else "Unknown",
                status=r.status.value,
                issue=r.description,
                created_at=r.created_at,
                completed_at=r.completed_at,
            )
            for r in repairs
        ]

    async def get_summary(self):
        r = await self.repo.get_summary()

        return RepairSummaryOut(
            total_repairs=r.total or 0,
            active_repairs=r.active or 0,
            completed_repairs=r.completed or 0,
        )
