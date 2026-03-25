from svc.persistence.session import get_session


def readiness_status(driver) -> dict[str, object]:
    checks: dict[str, dict[str, object]] = {}

    try:
        with get_session() as conn:
            conn.execute("SELECT 1").fetchone()
        checks["sqlite"] = {"status": "ok"}
    except Exception as error:  # noqa: BLE001
        checks["sqlite"] = {"status": "failed", "error": str(error)}

    try:
        fabrics = driver.collect_fabric_state()
        checks["ndfc"] = {"status": "ok", "fabrics": len(fabrics)}
    except Exception as error:  # noqa: BLE001
        checks["ndfc"] = {"status": "failed", "error": str(error)}

    overall = "ok" if all(check["status"] == "ok" for check in checks.values()) else "degraded"
    return {"status": overall, "checks": checks}
