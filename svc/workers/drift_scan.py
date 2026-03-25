from svc.persistence.session import get_session


def run() -> dict[str, object]:
    with get_session() as conn:
        rows = conn.execute(
            """
            SELECT fabric_name, serial_number, interface_name, COUNT(DISTINCT owner_service_key) AS owner_count
            FROM ownership_ledger
            GROUP BY fabric_name, serial_number, interface_name
            HAVING owner_count > 1
            """
        ).fetchall()

    conflicts = [dict(row) for row in rows]
    return {
        "status": "conflicts-found" if conflicts else "clean",
        "conflicts": conflicts,
        "count": len(conflicts),
    }
