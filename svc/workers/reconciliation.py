from svc.shared.clock import now_utc
from svc.workers.drift_scan import run as run_drift_scan


def run() -> dict[str, object]:
    drift = run_drift_scan()
    return {
        "generated_at": now_utc().isoformat(),
        "drift_status": drift["status"],
        "drift_count": drift["count"],
        "actions": [] if drift["count"] == 0 else ["manual-review-required"],
    }
