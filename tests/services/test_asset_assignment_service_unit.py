from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy.exc import DBAPIError

import services.assets.asset_assignment_service as module
from core.exceptions.errors import BadRequest, NotFound
from db.models.enums import AssetStatus, UserStatus
from schemas.auth import CurrentUserSchema
from services.assets.asset_assignment_service import AssetAssignmentService

pytestmark = pytest.mark.anyio


def _repo():
    repo = AsyncMock()
    repo.flush.return_value = None
    return repo


def _actor():
    return CurrentUserSchema(
        id=uuid4(), role="superadmin", permissions=["assets.update"]
    )


async def test_assign_asset_success(monkeypatch):
    actor_id = uuid4()
    asset_id = uuid4()
    user_id = uuid4()
    assigned_at = datetime.now(UTC)
    repo = _repo()
    repo.get_asset_for_update.return_value = SimpleNamespace(
        id=asset_id,
        owner_id=None,
        status=AssetStatus.ACTIVE,
        region_id=None,
        service_id=None,
        name="Test Asset",
    )
    repo.get_user.return_value = SimpleNamespace(
        id=user_id,
        status=UserStatus.ACTIVE.value,
        assigned_region_id=None,
        assigned_service_id=None,
    )
    repo.get_active_assignment.return_value = None
    repo.create_assignment.return_value = SimpleNamespace(
        assigned_at=assigned_at,
    )

    events = AsyncMock()
    service = AssetAssignmentService(repo, events)

    result = await service.assign_asset(asset_id, user_id, _actor())

    assert result.asset_id == asset_id
    assert result.user_id == user_id
    assert result.assigned_at == assigned_at
    repo.create_assignment.assert_awaited_once_with(asset_id, user_id)
    events.assigned.assert_awaited_once()


async def test_assign_asset_maps_lock_error(monkeypatch):
    class _LockError(Exception):
        pass

    actor_id = uuid4()
    asset_id = uuid4()
    user_id = uuid4()
    repo = _repo()
    monkeypatch.setattr(module.asyncpg.exceptions, "LockNotAvailableError", _LockError)
    repo.get_asset_for_update.side_effect = DBAPIError("stmt", {}, _LockError("locked"))
    service = AssetAssignmentService(repo, AsyncMock())

    with pytest.raises(BadRequest, match="Asset is locked"):
        await service.assign_asset(asset_id, user_id, _actor())


async def test_assign_asset_raises_for_missing_asset():
    repo = _repo()
    repo.get_asset_for_update.return_value = None
    service = AssetAssignmentService(repo, AsyncMock())

    with pytest.raises(NotFound, match="Asset not found"):
        await service.assign_asset(uuid4(), uuid4(), _actor())


async def test_unassign_asset_rejects_when_not_assigned():
    repo = _repo()
    repo.get_asset_for_update.return_value = SimpleNamespace(
        id=uuid4(),
        owner_id=None,
        status=AssetStatus.ACTIVE,
        region_id=None,
        service_id=None,
    )
    repo.get_active_assignment.return_value = None
    service = AssetAssignmentService(repo, AsyncMock())

    with pytest.raises(BadRequest, match="Asset is not currently assigned"):
        await service.unassign_asset(uuid4(), _actor())


async def test_reassign_asset_closes_active_and_delegates(monkeypatch):
    asset_id = uuid4()
    new_user_id = uuid4()
    actor = _actor()
    repo = _repo()
    repo.get_asset_for_update.return_value = SimpleNamespace(
        id=asset_id,
        region_id=None,
        service_id=None,
        owner_id=None,
        status=AssetStatus.ACTIVE,
    )
    repo.get_active_assignment.return_value = SimpleNamespace(id=uuid4())
    service = AssetAssignmentService(repo, AsyncMock())
    expected = SimpleNamespace(asset_id=asset_id, user_id=new_user_id)
    monkeypatch.setattr(service, "assign_asset", AsyncMock(return_value=expected))

    result = await service.reassign_asset(asset_id, new_user_id, actor)

    assert result is expected
    repo.close_assignment.assert_awaited_once()
    service.assign_asset.assert_awaited_once_with(
        asset_id,
        new_user_id,
        actor,
    )
