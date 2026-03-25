from datetime import datetime, timezone

_STARTED_AT = datetime.now(timezone.utc)


def liveness_status() -> dict[str, str]:
    now = datetime.now(timezone.utc)
    return {
        "status": "ok",
        "started_at": _STARTED_AT.isoformat(),
        "now": now.isoformat(),
    }
