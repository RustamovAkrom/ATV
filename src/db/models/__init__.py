# src/db/models/__init__.py

import pkgutil
import importlib
from pathlib import Path

_loaded = False  # 🔥 защита от повторной загрузки


def load_all_models() -> None:
    """
    Import all model modules to register them in SQLAlchemy registry.
    Safe to call multiple times.
    """
    global _loaded

    if _loaded:
        return

    package_dir = Path(__file__).resolve().parent

    for module in pkgutil.walk_packages(
        path=[str(package_dir)],
        prefix="db.models.",
    ):
        importlib.import_module(module.name)

    _loaded = True
