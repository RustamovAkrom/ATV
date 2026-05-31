import time

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from core.observability.prometheus import (
    APP_NAME,
    EXCEPTIONS_TOTAL,
    IN_PROGRESS,
    REQUEST_DURATION,
    REQUEST_ERRORS,
    REQUEST_STATUS_CLASS,
    REQUEST_TOTAL,
)


class MetricsMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app
        self.app_label = APP_NAME

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        # Игнорируем метрики и не-http запросы
        if scope["type"] != "http" or scope["path"].startswith("/metrics"):
            await self.app(scope, receive, send)
            return

        method = scope["method"]
        # Получаем путь роута или дефолтный путь
        route = scope.get("route")
        endpoint = route.path if route else scope["path"]

        start_time = time.perf_counter()
        IN_PROGRESS.labels(app=self.app_label).inc()

        async def send_wrapper(message: Message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                duration = time.perf_counter() - start_time
                status_str = str(status_code)

                # Записываем метрики
                REQUEST_TOTAL.labels(
                    app=self.app_label,
                    method=method,
                    endpoint=endpoint,
                    status=status_str,
                ).inc()

                REQUEST_DURATION.labels(
                    app=self.app_label, method=method, endpoint=endpoint
                ).observe(duration)

                REQUEST_STATUS_CLASS.labels(
                    app=self.app_label,
                    method=method,
                    endpoint=endpoint,
                    status_class=f"{status_code // 100}xx",
                ).inc()

                if status_code >= 400:
                    REQUEST_ERRORS.labels(
                        app=self.app_label,
                        method=method,
                        endpoint=endpoint,
                        status=status_str,
                    ).inc()

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception:
            EXCEPTIONS_TOTAL.labels(app=self.app_label, endpoint=endpoint).inc()
            raise
        finally:
            IN_PROGRESS.labels(app=self.app_label).dec()
