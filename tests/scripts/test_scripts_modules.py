from types import SimpleNamespace

import pytest


@pytest.mark.anyio
async def test_seed_rbac_runs_with_fake_db(monkeypatch):
    from scripts.bootstrap import rbac as module

    class _FakeResult:
        def __init__(self, items):
            self._items = items

        def scalars(self):
            return SimpleNamespace(all=lambda: self._items)

    class _FakeDB:
        def __init__(self):
            self.calls = []

        async def execute(self, *args, **kwargs):
            self.calls.append((args, kwargs))
            return _FakeResult([])

        def add(self, obj):
            return None

        async def flush(self):
            return None

    monkeypatch.setattr(
        module.Permissions, "all", staticmethod(lambda: ["users.view", "users.edit"])
    )

    db = _FakeDB()
    await module.seed_rbac(db)
    assert len(db.calls) >= 3


@pytest.mark.anyio
async def test_create_superadmin_validation_paths(monkeypatch):
    from scripts.users import create_superadmin as module

    inputs = iter(["", "", "", ""])  # empty login branch
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    class _DB:
        async def execute(self, *args, **kwargs):
            return SimpleNamespace(scalar_one_or_none=lambda: None)

    result = await module.create_superadmin(_DB())
    assert result is None


@pytest.mark.anyio
async def test_cleanup_expired_tokens_and_run(monkeypatch):
    import importlib
    import sys

    sys.modules["core.database"] = SimpleNamespace(get_session_factory=lambda: None)
    module = importlib.import_module("scripts.cleanup.tokens")

    class _Result:
        rowcount = 2

    class _Session:
        async def execute(self, *args, **kwargs):
            return _Result()

        def begin(self):
            return _Ctx()

    deleted = await module.cleanup_expired_tokens(_Session())
    assert deleted == 2

    class _Ctx:
        async def __aenter__(self):
            return _Session()

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def begin(self):
            return self

    class _Factory:
        def __call__(self):
            return _Ctx()

    monkeypatch.setattr(module, "get_sync_session_factory", lambda: _Factory())
    await module._run()


def test_runner_and_cli_and_entrypoints(monkeypatch):
    import importlib
    import sys

    import main
    from scripts import cli, runner

    async def _async_fn(session):
        return None

    class _Ctx:
        async def __aenter__(self):
            return object()

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def begin(self):
            return self

    class _Factory:
        def __call__(self):
            return _Ctx()

    monkeypatch.setattr(runner, "get_async_session_factory", lambda: _Factory())
    monkeypatch.setattr(runner.asyncio, "run", lambda coro: None)
    runner.run(_async_fn)

    called = []
    monkeypatch.setattr(cli, "run", lambda fn: called.append(fn.__name__))
    sys.modules["core.database"] = SimpleNamespace(get_session_factory=lambda: None)
    importlib.import_module("scripts.cleanup.tokens")

    cli.bootstrap()
    cli.create_superadmin()
    cli.cleanup_tokens()
    cli.init()
    assert len(called) >= 4

    uvicorn_called = {}
    monkeypatch.setattr(
        main,
        "get_settings",
        lambda: SimpleNamespace(APP_HOST="127.0.0.1", APP_PORT=8000, APP_RELOAD=False),
    )
    monkeypatch.setattr(
        main.uvicorn, "run", lambda *args, **kwargs: uvicorn_called.update(kwargs)
    )
    main.main()
    assert uvicorn_called.get("host") == "127.0.0.1"
