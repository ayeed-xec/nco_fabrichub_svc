import hashlib
import json
import uuid

from svc.persistence.session import get_session
from svc.schemas.api_v2 import PlanResponse


class PlanRepository:
    def create(self, plan):
        plan_id = str(uuid.uuid4())
        payload = {
            "service_order_id": getattr(plan, "service_order_id", ""),
            "operations": getattr(plan, "operations", []),
            "rollback_boundary": getattr(plan, "rollback_boundary", {}),
        }
        plan_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        record = PlanResponse(
            plan_id=plan_id,
            plan_hash=plan_hash,
            status="created",
            approval_required=True,
            operations=payload["operations"],
            rollback_boundary=payload["rollback_boundary"],
        )
        with get_session() as conn:
            conn.execute(
                """
                INSERT INTO plans (
                    plan_id, service_order_id, plan_hash, status, approval_required, operations_json, rollback_boundary_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.plan_id,
                    payload["service_order_id"],
                    record.plan_hash,
                    record.status,
                    1 if record.approval_required else 0,
                    json.dumps(record.operations),
                    json.dumps(record.rollback_boundary),
                ),
            )
        return record

    def get(self, plan_id: str):
        with get_session() as conn:
            row = conn.execute("SELECT * FROM plans WHERE plan_id = ?", (plan_id,)).fetchone()
        if row is None:
            raise KeyError(plan_id)
        return PlanResponse(
            plan_id=row["plan_id"],
            plan_hash=row["plan_hash"],
            status=row["status"],
            approval_required=bool(row["approval_required"]),
            operations=json.loads(row["operations_json"]),
            rollback_boundary=json.loads(row["rollback_boundary_json"]),
        )

    def _set_status(self, plan_id: str, status: str):
        with get_session() as conn:
            conn.execute("UPDATE plans SET status = ? WHERE plan_id = ?", (status, plan_id))
        return self.get(plan_id)

    def mark_previewed(self, plan_id: str):
        return self._set_status(plan_id, "previewed")

    def mark_approved(self, plan_id: str):
        return self._set_status(plan_id, "approved")

    def mark_deployed(self, plan_id: str):
        return self._set_status(plan_id, "deployed")

    def mark_rolled_back(self, plan_id: str):
        return self._set_status(plan_id, "rolled_back")
