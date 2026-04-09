from fastapi import FastAPI, APIRouter
from core.config import get_settings
from core.lifespan import lifespan
from core.observability.monitoring import router as monitoring_router
from core.exceptions.handlers import register_exception_handlers

def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        description=settings.APP_VERSION,
        root_path=settings.ROOT_PATH,
        lifespan=lifespan,
    )

    app.include_router(router=monitoring_router, tags=["Monitoring"])

    register_exception_handlers(app)

    return app
