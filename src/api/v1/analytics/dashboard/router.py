from fastapi import APIRouter

from .regions import router as regions_router
from .top_assets import router as top_asset_router
from .repairs import router as repairs_router
from .services import router as services_router
from .overview import router as overview_router

router = APIRouter(prefix="/analytics/dashboard", tags=["Analytics - Dashboard"])


router.include_router(overview_router)
router.include_router(regions_router)
router.include_router(top_asset_router)
router.include_router(repairs_router)
router.include_router(services_router)
