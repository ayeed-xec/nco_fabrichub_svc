import uuid

from svc.persistence.session import get_session


class OwnershipRepository:
    def find_for_service_intent(self, service_intent):
        conflicts = []
        service_key = f"{service_intent.tenant_name}:{service_intent.service_name}"

        with get_session() as conn:
            rows = conn.execute(
                "SELECT fabric_name, serial_number, interface_name, owner_service_key FROM ownership_ledger WHERE fabric_name = ?",
                (service_intent.fabric_name,),
            ).fetchall()

        for row in rows:
            for endpoint in service_intent.endpoints:
                if (
                    row["serial_number"] == endpoint.serial_number
                    and row["interface_name"] == endpoint.interface_name
                    and row["owner_service_key"] != service_key
                ):
                    conflicts.append(
                        {
                            "object_type": "interface-policy",
                            "object_name": endpoint.interface_name,
                            "owner_service_key": row["owner_service_key"],
                        }
                    )

        if service_intent.flags.get("simulate_ownership_conflict"):
            conflicts.append(
                {
                    "object_type": "interface-policy",
                    "object_name": service_intent.endpoints[0].interface_name,
                    "owner_service_key": "other-tenant:other-service",
                }
            )

        return conflicts

    def claim_from_plan(self, plan: object):
        boundary = getattr(plan, "rollback_boundary", {})
        with get_session() as conn:
            for item in boundary.get("interfaces", []):
                conn.execute(
                    """
                    INSERT INTO ownership_ledger (ownership_id, fabric_name, serial_number, interface_name, owner_service_key)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid.uuid4()),
                        boundary.get("fabric_name"),
                        item["serial_number"],
                        item["interface_name"],
                        boundary.get("service_key"),
                    ),
                )
