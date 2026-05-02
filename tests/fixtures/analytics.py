from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from core.security.jwt import create_access_token
from db.models.enums import AssetStatus, TransferStatus, UserRole
from tests.factories.analytics import (
    create_asset,
    create_assignment,
    create_history,
    create_org_graph,
    create_repair,
    create_transfer,
    create_user_with_role,
)
from utils.helpers import utc_now


@pytest.fixture
async def analytics_users(dbsession):
    superadmin = await create_user_with_role(
        dbsession, login_prefix="superadmin", role_code=UserRole.SUPERADMIN.value
    )
    admin = await create_user_with_role(
        dbsession, login_prefix="admin", role_code=UserRole.ADMIN.value
    )
    analytic = await create_user_with_role(
        dbsession, login_prefix="analytic", role_code=UserRole.ANALYTIC.value
    )
    moderator = await create_user_with_role(
        dbsession, login_prefix="moderator", role_code=UserRole.MODERATOR.value
    )
    # Removed commit - let test session handle transaction
    return {
        "superadmin": superadmin,
        "admin": admin,
        "analytic": analytic,
        "moderator": moderator,
    }


@pytest.fixture
async def analytics_tokens(client, analytics_users):
    tokens = {}
    for key, user in analytics_users.items():
        tokens[key] = create_access_token(str(user.id), str(uuid4()))
    return tokens


@pytest.fixture
async def analytics_seed(dbsession, analytics_users):
    graph = await create_org_graph(dbsession)
    now = utc_now()

    asset_primary = await create_asset(
        dbsession,
        graph=graph,
        owner=analytics_users["admin"],
        name="PrimaryAsset",
        status=AssetStatus.ASSIGNED,
        purchase_cost=Decimal("2000"),
    )
    asset_secondary = await create_asset(
        dbsession,
        graph=graph,
        owner=analytics_users["analytic"],
        name="SecondaryAsset",
        status=AssetStatus.IN_REPAIR,
        purchase_cost=Decimal("500"),
    )
    asset_tertiary = await create_asset(
        dbsession,
        graph=graph,
        owner=analytics_users["admin"],
        name="TertiaryAsset",
        status=AssetStatus.ACTIVE,
        purchase_cost=Decimal("300"),
    )

    await create_assignment(
        dbsession,
        asset=asset_primary,
        user=analytics_users["admin"],
        assigned_at=now - timedelta(days=10),
        unassigned_at=None,
    )
    await create_assignment(
        dbsession,
        asset=asset_primary,
        user=analytics_users["analytic"],
        assigned_at=now - timedelta(days=20),
        unassigned_at=now - timedelta(days=12),
    )
    await create_assignment(
        dbsession,
        asset=asset_secondary,
        user=analytics_users["analytic"],
        assigned_at=now - timedelta(days=5),
        unassigned_at=None,
    )
    await create_assignment(
        dbsession,
        asset=asset_tertiary,
        user=analytics_users["admin"],
        assigned_at=now - timedelta(days=4),
        unassigned_at=None,
    )

    await create_transfer(
        dbsession,
        asset=asset_primary,
        created_by=analytics_users["admin"],
        graph=graph,
        created_at=now - timedelta(days=9),
        status=TransferStatus.COMPLETED,
        transferred_at=now - timedelta(days=7),
    )
    await create_transfer(
        dbsession,
        asset=asset_secondary,
        created_by=analytics_users["analytic"],
        graph=graph,
        created_at=now - timedelta(days=8),
        status=TransferStatus.PENDING,
    )

    await create_repair(
        dbsession,
        asset=asset_primary,
        reported_by=analytics_users["admin"],
        created_at=now - timedelta(days=6),
        labor_cost=Decimal("150"),
        parts_cost=Decimal("50"),
    )
    await create_repair(
        dbsession,
        asset=asset_secondary,
        reported_by=analytics_users["analytic"],
        created_at=now - timedelta(days=3),
        labor_cost=Decimal("80"),
        parts_cost=Decimal("20"),
    )

    await create_history(
        dbsession,
        asset=asset_primary,
        user=analytics_users["admin"],
        action="assigned",
        description="Asset assigned",
        created_at=now - timedelta(days=10),
    )
    await create_history(
        dbsession,
        asset=asset_secondary,
        user=analytics_users["analytic"],
        action="repair_finished",
        description="Repair completed",
        created_at=now - timedelta(days=2),
    )

    # Removed commit - let test session handle transaction
    return {
        "graph": graph,
        "asset_primary": asset_primary,
        "asset_secondary": asset_secondary,
        "asset_tertiary": asset_tertiary,
        "now": now,
    }
