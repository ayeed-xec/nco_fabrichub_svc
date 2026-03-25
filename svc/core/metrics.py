from fastapi import FastAPI
from prometheus_client import make_asgi_app


def register_metrics(app: FastAPI) -> None:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
