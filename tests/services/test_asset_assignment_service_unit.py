from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy.exc import DBAPIError

from core.exceptions.errors import BadRequest, NotFound
from db.models.enums import AssetStatus, UserStatus
from services import asset_assignment_service as module
from services.asset_assignment_service import AssetAssignmentService

pytestmark = pytest.mark.anyio


def _repo():
    repo = AsyncMock()
    repo.flush.return_value = None
    repo.add_history.return_value = None
    return repo


async def test_assign_asset_success(monkeypatch):
    actor_id = uuid4()
    asset_id = uuid4()
    user_id = uuid4()
    assigned_at = datetime.now(timezone.utc)
    repo = _repo()
    repo.get_asset_for_update.return_value = SimpleNamespace(
        id=asset_id, owner_id=None, status=AssetStatus.ACTIVE
    )
    repo.get_user.return_value = SimpleNamespace(id=user_id, status=UserStatus.ACTIVE.value)
    repo.get_active_assignment.return_value = None
    repo.create_assignment.return_value = SimpleNamespace(assigned_at=assigned_at)

    service = AssetAssignmentService(repo)
    monkeypatch.setattr(module.audit_stream, "publish", AsyncMock())

    result = await service.assign_asset(asset_id, user_id, actor_id)

    assert result.asset_id == asset_id
    assert result.user_id == user_id
    assert result.assigned_at == assigned_at
    repo.create_assignment.assert_awaited_once_with(asset_id, user_id)
    repo.add_history.assert_awaited()


async def test_assign_asset_maps_lock_error(monkeypatch):
    class _LockError(Exception):
        pass

    actor_id = uuid4()
    asset_id = uuid4()
    user_id = uuid4()
    repo = _repo()
    monkeypatch.setattr(module.asyncpg.exceptions, "LockNotAvailableError", _LockError)
    repo.get_asset_for_update.side_effect = DBAPIError("stmt", {}, _LockError("locked"))
    service = AssetAssignmentService(repo)

    with pytest.raises(BadRequest, match="Asset is locked"):
        await service.assign_asset(asset_id, user_id, actor_id)


@pytest.mark.parametrize(
    ("active_user_id", "message"),
    [
        ("same", "Asset is already assigned to this user"),
        ("different", "Asset already assigned"),
    ],
)
async def test_assign_asset_rejects_when_active_assignment_exists(active_user_id, message):
    actor_id = uuid4()
    asset_id = uuid4()
    user_id = uuid4()
    current_user_id = user_id if active_user_id == "same" else uuid4()
    repo = _repo()
    repo.get_asset_for_update.return_value = SimpleNamespace(
        id=asset_id, owner_id=None, status=AssetStatus.ACTIVE
    )
    repo.get_user.return_value = SimpleNamespace(id=user_id, status=UserStatus.ACTIVE.value)
    repo.get_active_assignment.return_value = SimpleNamespace(user_id=current_user_id)
    service = AssetAssignmentService(repo)

    with pytest.raises(BadRequest, match=message):
        await service.assign_asset(asset_id, user_id, actor_id)


async def test_assign_asset_raises_for_missing_asset():
    repo = _repo()
    repo.get_asset_for_update.return_value = None
    service = AssetAssignmentService(repo)

    with pytest.raises(NotFound, match="Asset not found"):
        await service.assign_asset(uuid4(), uuid4(), uuid4())


async def test_unassign_asset_falls_back_to_plain_lookup(monkeypatch):
    actor_id = uuid4()
    asset_id = uuid4()
    owner_id = uuid4()
    timestamp = datetime.now(timezone.utc)
    repo = _repo()
    repo.get_asset_for_update.return_value = None
    repo.get_asset_plain.return_value = SimpleNamespace(
        id=asset_id, owner_id=owner_id, status=AssetStatus.ASSIGNED
    )
    repo.get_active_assignment.return_value = SimpleNamespace(asset_id=asset_id, user_id=owner_id)
    monkeypatch.setattr(module, "utc_now", lambda: timestamp)
    service = AssetAssignmentService(repo)
    monkeypatch.setattr(module.audit_stream, "publish", AsyncMock())

    result = await service.unassign_asset(asset_id, actor_id)

    assert result.asset_id == asset_id
    assert result.user_id == owner_id
    assert result.unassigned_at == timestamp
    repo.close_assignment.assert_awaited_once()


async def test_unassign_asset_rejects_when_not_assigned():
    repo = _repo()
    repo.get_asset_for_update.return_value = SimpleNamespace(
        id=uuid4(), owner_id=None, status=AssetStatus.ACTIVE
    )
    repo.get_active_assignment.return_value = None
    service = AssetAssignmentService(repo)

    with pytest.raises(BadRequest, match="Asset is not currently assigned"):
        await service.unassign_asset(uuid4(), uuid4())


async def test_reassign_asset_closes_active_and_delegates(monkeypatch):
    asset_id = uuid4()
    actor_id = uuid4()
    new_user_id = uuid4()
    repo = _repo()
    repo.get_asset_for_update.return_value = SimpleNamespace(id=asset_id)
    repo.get_active_assignment.return_value = SimpleNamespace(id=uuid4())
    service = AssetAssignmentService(repo)
    expected = SimpleNamespace(asset_id=asset_id, user_id=new_user_id)
    monkeypatch.setattr(service, "assign_asset", AsyncMock(return_value=expected))

    result = await service.reassign_asset(asset_id, new_user_id, actor_id)

    assert result is expected
    repo.close_assignment.assert_awaited_once()
    service.assign_asset.assert_awaited_once_with(asset_id, new_user_id, actor_id)
