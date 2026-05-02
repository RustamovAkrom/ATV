from core.admin.base import BaseAdmin
from db.models.org.rank import Rank
from db.models.org.region import Region
from db.models.org.service import Service


class RankAdmin(BaseAdmin, model=Rank):
    name = "Rank"
    name_plural = "Ranks"
    icon = "fa-solid fa-star"

    column_list = ["id", "name", "code", "created_at"]


class RegionAdmin(BaseAdmin, model=Region):
    name = "Region"
    name_plural = "Regions"
    icon = "fa-solid fa-map"

    column_list = [
        "id",
        "name",
        "latitude",
        "longitude",
        "geojson",
        "created_at",
    ]


class ServiceAdmin(BaseAdmin, model=Service):
    name = "Service"
    name_plural = "Services"
    icon = "fa-solid fa-cogs"

    column_list = ["id", "name", "code", "created_at"]
