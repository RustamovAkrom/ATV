from unittest.mock import AsyncMock

import pytest
from sqlalchemy.exc import IntegrityError

from core.exceptions.errors import BadRequest
from utils import validators


def test_validate_name_strips_and_returns_value():
    assert validators.validate_name("  Asset A  ") == "Asset A"


@pytest.mark.parametrize(
    ("name", "message"),
    [
        ("", "Name cannot be empty"),
        (" ", "Name cannot be empty"),
        ("a", "Name too short"),
        ("!" * 101, "Name is too long"),
        ("!!!", "Invalid name"),
    ],
)
def test_validate_name_rejects_invalid_values(name, message):
    with pytest.raises(BadRequest, match=message):
        validators.validate_name(name)


def test_normalize_name():
    assert validators.normalize_name("  My Name  ") == "my name"


@pytest.mark.anyio
async def test_ensure_unique_name_raises_when_found():
    repo = AsyncMock()
    repo.get_by_normalized_name.return_value = object()

    with pytest.raises(BadRequest, match="Already exists"):
        await validators.ensure_unique_name(repo, "name")


@pytest.mark.anyio
async def test_ensure_unique_code_raises_when_found():
    repo = AsyncMock()
    repo.get_by_code.return_value = object()

    with pytest.raises(BadRequest, match="Similar entity already exists"):
        await validators.ensure_unique_code(repo, "code")


@pytest.mark.anyio
async def test_safe_create_returns_repo_result():
    repo = AsyncMock()
    repo.create.return_value = {"id": 1}

    assert await validators.safe_create(repo, {"name": "ok"}) == {"id": 1}


@pytest.mark.anyio
async def test_safe_create_maps_integrity_error():
    repo = AsyncMock()
    repo.create.side_effect = IntegrityError("stmt", {}, Exception("dup"))

    with pytest.raises(BadRequest, match="Already exists"):
        await validators.safe_create(repo, {"name": "dup"})


@pytest.mark.anyio
async def test_safe_create_maps_unknown_error():
    repo = AsyncMock()
    repo.create.side_effect = RuntimeError("boom")

    with pytest.raises(BadRequest, match="Failed to create"):
        await validators.safe_create(repo, {"name": "boom"})


@pytest.mark.anyio
async def test_validate_and_prepare_success():
    repo = AsyncMock()
    repo.get_by_normalized_name.return_value = None
    repo.get_by_code.return_value = None

    name, code = await validators.validate_and_prepare(repo, " Main Office ")

    assert name == "Main Office"
    assert code == "main_office"
    repo.get_by_normalized_name.assert_awaited_once_with("main office")
    repo.get_by_code.assert_awaited_once_with("main_office")


@pytest.mark.anyio
async def test_validate_and_prepare_rejects_empty_slug(monkeypatch):
    repo = AsyncMock()
    repo.get_by_normalized_name.return_value = None
    monkeypatch.setattr(validators, "slugify", lambda _name: "")

    with pytest.raises(BadRequest, match="Invalid name"):
        await validators.validate_and_prepare(repo, "Valid Name")
