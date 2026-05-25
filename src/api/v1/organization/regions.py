from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from api.dependencies.organizations.regions import get_region_service
from core.cache.decorators import cached, invalidate_cache
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import RegionPermissions
from core.slowapi import limiter
from schemas.auth.auth import CurrentUserSchema
from schemas.organization.region import (
    RegionCreateSchema,
    RegionOutSchema,
    RegionTreeOutSchema,
    RegionUpdateSchema,
)
from services.organization.region_service import RegionService

router = APIRouter(prefix="/regions", tags=["Regions"])


@router.get(
    "/tree",
    response_model=list[RegionTreeOutSchema],
    dependencies=[Depends(RegionPermissions.CanViewRegions)],
)
@cached(ttl=30, tags=("region:tree",))
async def get_regions_tree(
    service: RegionService = Depends(get_region_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Get regions as hierarchical tree structure."""
    return await service.get_tree()


@router.get(
    "/",
    response_model=list[RegionOutSchema],
    dependencies=[Depends(RegionPermissions.CanViewRegions)],
)
@cached(ttl=30, tags=("region:list",))
async def list_regions(
    service: RegionService = Depends(get_region_service),
    _: CurrentUserSchema = Depends(get_current_user),
    level: int | None = Query(None, ge=1, le=4),
    parent_id: UUID | None = None,
):
    """List all regions with optional filtering."""
    return await service.list(level=level, parent_id=parent_id)


@router.get(
    "/{region_id}",
    response_model=RegionOutSchema,
    dependencies=[Depends(RegionPermissions.CanViewRegions)],
)
@cached(ttl=30, tags=("region:detail",))
async def get_region(
    region_id: UUID,
    service: RegionService = Depends(get_region_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Get a specific region by ID."""
    return await service.get(region_id)


@router.post(
    "/",
    response_model=RegionOutSchema,
    dependencies=[Depends(RegionPermissions.CanCreateRegions)],
)
@limiter.limit("10/minute")
@invalidate_cache(
    tags=(
        "region:tree",
        "region:list",
    )
)
async def create_region(
    request: Request,
    data: RegionCreateSchema,
    service: RegionService = Depends(get_region_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """Create a new region."""
    return await service.create(data, current_user.id)


@router.patch(
    "/{region_id}",
    response_model=RegionOutSchema,
    dependencies=[Depends(RegionPermissions.CanUpdateRegions)],
)
@limiter.limit("20/minute")
@invalidate_cache(
    tags=(
        "region:tree",
        "region:list",
        "region:detail",
    )
)
async def update_region(
    request: Request,
    region_id: UUID,
    data: RegionUpdateSchema,
    service: RegionService = Depends(get_region_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Update an existing region."""
    return await service.update(region_id, data)


@router.delete(
    "/{region_id}",
    response_model=dict[str, Any],
    dependencies=[Depends(RegionPermissions.CanDeleteRegions)],
)
@limiter.limit("5/minute")
@invalidate_cache(
    tags=(
        "region:tree",
        "region:list",
        "region:detail",
    )
)
async def delete_region(
    request: Request,
    region_id: UUID,
    service: RegionService = Depends(get_region_service),
    _: CurrentUserSchema = Depends(get_current_user),
):
    """Delete a region (only if no children)."""
    return await service.delete(region_id)
