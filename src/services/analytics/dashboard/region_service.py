from schemas.analytics.dashboard.region import RegionDistributionOut, RegionMetrics


class RegionAnalyticsService:
    def __init__(self, repo):
        self.repo = repo

    async def get_region_distribution(self):
        rows = await self.repo.get_region_stats()

        result = []

        for r in rows:
            total = r.total or 0
            active = r.active or 0

            result.append(
                RegionDistributionOut(
                    region_id=r.id,
                    region_name=r.name,
                    metrics=RegionMetrics(
                        total=total,
                        active=active,
                        inactive=r.archived or 0,
                        repair=r.repair or 0,
                    ),
                    health_score=(active / total) if total else 0,
                    latitude=r.latitude,
                    longitude=r.longitude,
                    geojson=r.geojson,
                )
            )

        return result
