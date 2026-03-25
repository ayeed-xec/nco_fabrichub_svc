from fastapi import FastAPI

from svc.api.v1.compat import router as v1_compat_router
from svc.api.v1.health import router as v1_health_router
from svc.api.v2.router import router as v2_router
from svc.core.logging import configure_logging
from svc.core.metrics import register_metrics
from svc.core.settings import get_settings
from svc.persistence.session import initialize_schema


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)

    app = FastAPI(
        title="nco-fabrichub-svc",
        version="2.0.0",
        docs_url="/docs" if settings.enable_docs else None,
        redoc_url=None,
    )

    initialize_schema()

    register_metrics(app)

    app.include_router(v1_health_router, prefix="/api/v1")
    app.include_router(v1_compat_router, prefix="/api/v1")
    app.include_router(v2_router, prefix="/api/v2")

    return app
