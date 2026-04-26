from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from repositories.assets.asset_assignment_repo import AssetAssignmentRepository

pytestmark = pytest.mark.anyio


async def test_get_asset_returns_scalar_one_or_none():
    scalar = object()
    result = SimpleNamespace(scalar_one_or_none=lambda: scalar)
    session = SimpleNamespace(execute=AsyncMock(return_value=result))
    repo = AssetAssignmentRepository(session)

    fetched = await repo.get_asset(uuid4())

    assert fetched is scalar
    session.execute.assert_awaited_once()


async def test_get_asset_for_update_returns_none_when_row_missing(monkeypatch):
    session = SimpleNamespace(
        execute=AsyncMock(return_value=SimpleNamespace(first=lambda: None))
    )
    repo = AssetAssignmentRepository(session)
    get_plain = AsyncMock()
    monkeypatch.setattr(repo, "get_asset_plain", get_plain)

    fetched = await repo.get_asset_for_update(uuid4())

    assert fetched is None
    get_plain.assert_not_called()


async def test_get_asset_for_update_fetches_plain_row(monkeypatch):
    asset = object()
    session = SimpleNamespace(
        execute=AsyncMock(return_value=SimpleNamespace(first=lambda: ("present",)))
    )
    repo = AssetAssignmentRepository(session)
    get_plain = AsyncMock(return_value=asset)
    monkeypatch.setattr(repo, "get_asset_plain", get_plain)
    asset_id = uuid4()

    fetched = await repo.get_asset_for_update(asset_id, nowait=True)

    assert fetched is asset
    get_plain.assert_awaited_once_with(asset_id)


async def test_create_assignment_adds_and_flushes():
    session = SimpleNamespace(add=Mock(), flush=AsyncMock())
    repo = AssetAssignmentRepository(session)
    asset_id = uuid4()
    user_id = uuid4()

    created = await repo.create_assignment(asset_id, user_id)

    assert created.asset_id == asset_id
    assert created.user_id == user_id
    session.add.assert_called_once()
    session.flush.assert_awaited_once()


async def test_close_assignment_sets_unassigned_at():
    session = SimpleNamespace(flush=AsyncMock())
    repo = AssetAssignmentRepository(session)
    timestamp = datetime.now(UTC)
    assignment = SimpleNamespace(unassigned_at=None)

    closed = await repo.close_assignment(assignment, timestamp)

    assert closed.unassigned_at == timestamp
    session.flush.assert_awaited_once()


async def test_add_history_adds_and_flushes():
    session = SimpleNamespace(add=Mock(), flush=AsyncMock())
    repo = AssetAssignmentRepository(session)
    asset_id = uuid4()
    user_id = uuid4()

    entry = await repo.add_history(asset_id, user_id, "assigned", "desc")

    assert entry.asset_id == asset_id
    assert entry.user_id == user_id
    assert entry.action == "assigned"
    session.add.assert_called_once()
    session.flush.assert_awaited_once()
