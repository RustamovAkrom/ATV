import time

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class LoggingMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.perf_counter()
        state = scope.get("state", {})
        logger = state.get("logger")  # Берем логгер, созданный в RequestIDMiddleware

        path = scope["path"]
        method = scope["method"]

        if logger:
            logger.info(f"{method} {path} - started")

        async def send_wrapper(message: Message):
            if message["type"] == "http.response.start":
                duration = round((time.perf_counter() - start_time) * 1000, 2)
                status = message["status"]
                if logger:
                    logger.info(
                        f"{method} {path} - completed",
                        status_code=status,
                        duration_ms=duration,
                    )
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as exc:
            if logger:
                logger.exception("Request failed", error=str(exc))
            raise
