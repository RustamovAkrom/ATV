from schemas.analytics.dashboard.top_assets import TopAssetOut
from repositories.analytics.dashboard.top_assets_repo import TopAssetsRepository


class TopAssetsService:
    def __init__(self, repo: TopAssetsRepository):
        self.repo = repo

    async def get_top_assets(self):
        rows = await self.repo.get_top_assets()

        return [
            TopAssetOut(
                asset_name=r.name,
                count=r.count,
            )
            for r in rows
        ]
