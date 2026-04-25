"""
Run FastAPI app with uvicorn.
    uv run src/main.py
"""

import uvicorn

from core.config import get_settings


def main() -> None:
    settings = get_settings()

    uvicorn.run(
        "app:create_app",
        app_dir="src",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_RELOAD,
    )


if __name__ == "__main__":
    main()
