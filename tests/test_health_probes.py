from svc.core.liveness import liveness_status
from svc.core.readiness import readiness_status


class _Driver:
    def __init__(self, raise_error: bool = False):
        self.raise_error = raise_error

    def collect_fabric_state(self):
        if self.raise_error:
            raise RuntimeError("provider unavailable")
        return [{"name": "fab-1", "state": "managed"}]


def test_liveness_reports_ok_and_timestamps():
    payload = liveness_status()
    assert payload["status"] == "ok"
    assert "started_at" in payload
    assert "now" in payload


def test_readiness_ok_when_sqlite_and_driver_available():
    payload = readiness_status(_Driver())
    assert payload["status"] == "ok"
    assert payload["checks"]["sqlite"]["status"] == "ok"
    assert payload["checks"]["ndfc"]["status"] == "ok"


def test_readiness_degraded_when_driver_unavailable():
    payload = readiness_status(_Driver(raise_error=True))
    assert payload["status"] == "degraded"
    assert payload["checks"]["ndfc"]["status"] == "failed"
