from pydantic import BaseModel


class TopAssetOut(BaseModel):
    asset_name: str
    count: int
