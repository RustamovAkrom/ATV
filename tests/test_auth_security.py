from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from api.v1 import security as security_api
from services.auth_service import AuthService


@pytest.mark.anyio
async def test_logout_accepts_matching_uuid_subjects(monkeypatch: pytest.MonkeyPatch) -> None:
    user_id = uuid4()
    refresh_jti = uuid4()
    access_jti = uuid4()

    blacklist = SimpleNamespace(add=AsyncMock())
    monkeypatch.setattr("services.auth_service.get_blacklist", lambda: blacklist)
    monkeypatch.setattr(
        "services.auth_service.decode_token",
        AsyncMock(return_value={"sub": user_id, "jti": refresh_jti, "type": "refresh"}),
    )

    service = AuthService(
        user_repo=AsyncMock(),
        auth_repo=SimpleNamespace(revoke=AsyncMock()),
    )

    await service.logout(
        "refresh-token",
        {
            "sub": user_id,
            "jti": access_jti,
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=15)).timestamp()),
        },
    )

    blacklist.add.assert_awaited_once()
    service.auth_repo.revoke.assert_awaited_once_with(refresh_jti)


@pytest.mark.anyio
async def test_refresh_rejects_subject_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    token_jti = uuid4()
    token_user_id = uuid4()
    payload_user_id = uuid4()

    monkeypatch.setattr(
        "services.auth_service.decode_token",
        AsyncMock(return_value={"sub": payload_user_id, "jti": token_jti, "type": "refresh"}),
    )

    auth_repo = SimpleNamespace(
        get_by_id=AsyncMock(
            return_value=SimpleNamespace(
                user_id=token_user_id,
                is_revoked=False,
                expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            )
        ),
        revoke_all_by_user=AsyncMock(),
        revoke=AsyncMock(),
        create=AsyncMock(),
    )
    service = AuthService(user_repo=AsyncMock(), auth_repo=auth_repo)

    with pytest.raises(Exception) as exc_info:
        await service.refresh("refresh-token")

    assert exc_info.value.detail == "Token subject mismatch"
    auth_repo.revoke_all_by_user.assert_awaited_once_with(token_user_id)
    auth_repo.revoke.assert_not_called()


@pytest.mark.anyio
async def test_logout_all_blacklists_current_access_token(monkeypatch: pytest.MonkeyPatch) -> None:
    user_id = uuid4()
    access_jti = uuid4()
    blacklist = SimpleNamespace(add=AsyncMock())
    auth_repo = SimpleNamespace(revoke_all_by_user=AsyncMock())

    monkeypatch.setattr("services.auth_service.get_blacklist", lambda: blacklist)

    service = AuthService(user_repo=AsyncMock(), auth_repo=auth_repo)
    await service.logout_all(
        user_id,
        {
            "sub": user_id,
            "jti": access_jti,
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=15)).timestamp()),
        },
    )

    blacklist.add.assert_awaited_once()
    auth_repo.revoke_all_by_user.assert_awaited_once_with(user_id)


@pytest.mark.anyio
async def test_forgot_password_hides_token_outside_debug_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_service = SimpleNamespace(request_password_reset=AsyncMock(return_value="secret-reset-token"))
    monkeypatch.setattr(security_api.settings, "ENV", "prod", raising=False)

    response = await security_api.forgot_password(
        security_api.ForgotPasswordRequest(login="demo"),
        service=mock_service,
    )

    assert response == {"status": "ok"}


@pytest.mark.anyio
async def test_forgot_password_exposes_debug_token_in_test_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mock_service = SimpleNamespace(request_password_reset=AsyncMock(return_value="secret-reset-token"))
    monkeypatch.setattr(security_api.settings, "ENV", "test", raising=False)

    response = await security_api.forgot_password(
        security_api.ForgotPasswordRequest(login="demo"),
        service=mock_service,
    )

    assert response == {"status": "ok", "debug_token": "secret-reset-token"}
