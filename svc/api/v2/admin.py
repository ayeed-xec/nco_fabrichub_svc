from fastapi import APIRouter

from svc.core.liveness import liveness_status
from svc.core.readiness import readiness_status
from svc.core.settings import get_settings
from svc.providers.ndfc.driver import NdfcDriver
from svc.workers.drift_scan import run as run_drift_scan

router = APIRouter()


def _build_driver() -> NdfcDriver:
    settings = get_settings()
    return NdfcDriver.from_settings(settings)


@router.get("/admin/readiness")
def readiness() -> dict[str, object]:
    return readiness_status(_build_driver())


@router.get("/admin/liveness")
def liveness() -> dict[str, str]:
    return liveness_status()


@router.get("/admin/drift-report")
def drift_report() -> dict[str, object]:
    return run_drift_scan()
