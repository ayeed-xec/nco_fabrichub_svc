import json
import uuid

from svc.persistence.session import get_session
from svc.schemas.api_v2 import DeploymentResponse, VerificationResponse


class _PendingDeployment:
    def __init__(self, deployment_id: str, plan_id: str):
        self.deployment_id = deployment_id
        self.plan_id = plan_id


class DeploymentRepository:
    def create_pending(self, plan_id: str, actor: str):
        deployment_id = str(uuid.uuid4())
        with get_session() as conn:
            conn.execute(
                "INSERT INTO deployments (deployment_id, plan_id, status, jobs_json) VALUES (?, ?, ?, ?)",
                (deployment_id, plan_id, "pending", json.dumps([])),
            )
        return _PendingDeployment(deployment_id=deployment_id, plan_id=plan_id)

    def mark_started(self, deployment_id: str, jobs: list[dict]):
        with get_session() as conn:
            conn.execute(
                "UPDATE deployments SET status = ?, jobs_json = ?, updated_at = CURRENT_TIMESTAMP WHERE deployment_id = ?",
                ("started", json.dumps(jobs), deployment_id),
            )

    def mark_completed(self, deployment_id: str, jobs: list[dict]):
        with get_session() as conn:
            conn.execute(
                "UPDATE deployments SET status = ?, jobs_json = ?, updated_at = CURRENT_TIMESTAMP WHERE deployment_id = ?",
                ("completed", json.dumps(jobs), deployment_id),
            )

    def mark_rolled_back(self, deployment_id: str):
        with get_session() as conn:
            conn.execute(
                "UPDATE deployments SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE deployment_id = ?",
                ("rolled_back", deployment_id),
            )

    def save_verification(self, verification: VerificationResponse):
        with get_session() as conn:
            conn.execute(
                "UPDATE deployments SET verification_json = ?, updated_at = CURRENT_TIMESTAMP WHERE deployment_id = ?",
                (verification.model_dump_json(), verification.deployment_id),
            )

    def get(self, deployment_id: str):
        with get_session() as conn:
            row = conn.execute("SELECT * FROM deployments WHERE deployment_id = ?", (deployment_id,)).fetchone()
        if row is None:
            raise KeyError(deployment_id)
        return DeploymentResponse(
            deployment_id=row["deployment_id"],
            plan_id=row["plan_id"],
            status=row["status"],
            jobs=json.loads(row["jobs_json"]),
        )

    def get_verification(self, deployment_id: str):
        with get_session() as conn:
            row = conn.execute("SELECT verification_json FROM deployments WHERE deployment_id = ?", (deployment_id,)).fetchone()
        if row is None or not row["verification_json"]:
            return VerificationResponse(deployment_id=deployment_id, status="pending", checks=[])
        return VerificationResponse.model_validate_json(row["verification_json"])

    def has_newer_completed_deployment(self, plan_id: str, deployment_id: str) -> bool:
        with get_session() as conn:
            row = conn.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM deployments newer
                    JOIN deployments current ON current.deployment_id = ?
                    WHERE newer.plan_id = ?
                      AND newer.status = 'completed'
                      AND newer.rowid > current.rowid
                ) AS has_newer
                """,
                (deployment_id, plan_id),
            ).fetchone()
        return bool(row["has_newer"])

    def has_inflight_for_service(self, service_key: str) -> bool:
        with get_session() as conn:
            row = conn.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM deployments d
                    JOIN plans p ON p.plan_id = d.plan_id
                    WHERE d.status IN ('pending', 'started')
                      AND p.rollback_boundary_json LIKE ?
                ) AS has_inflight
                """,
                (f'%"service_key": "{service_key}"%',),
            ).fetchone()
        return bool(row["has_inflight"])
