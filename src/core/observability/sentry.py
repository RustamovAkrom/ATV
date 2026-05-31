import sentry_sdk

from core.config import get_settings


def init_sentry() -> None:
    settings = get_settings()

    if not settings.SENTRY_DSN:
        return

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENV,
        traces_sample_rate=0.1,
        send_default_pii=True,
        debug=settings.DEBUG,
    )
