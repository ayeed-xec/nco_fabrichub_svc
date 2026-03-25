from svc.persistence.session import get_session
from svc.shared.ids import new_id


class EvidenceRepository:
    def add_artifact(self, deployment_id: str, artifact_type: str, artifact_path: str, checksum: str) -> dict:
        artifact = {
            "artifact_id": new_id(),
            "deployment_id": deployment_id,
            "artifact_type": artifact_type,
            "artifact_path": artifact_path,
            "checksum": checksum,
        }
        with get_session() as conn:
            conn.execute(
                """
                INSERT INTO evidence_artifacts (artifact_id, deployment_id, artifact_type, artifact_path, checksum)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    artifact["artifact_id"],
                    artifact["deployment_id"],
                    artifact["artifact_type"],
                    artifact["artifact_path"],
                    artifact["checksum"],
                ),
            )
        return artifact

    def list_for_deployment(self, deployment_id: str) -> list[dict]:
        with get_session() as conn:
            rows = conn.execute(
                "SELECT artifact_id, deployment_id, artifact_type, artifact_path, checksum FROM evidence_artifacts WHERE deployment_id = ?",
                (deployment_id,),
            ).fetchall()
        return [dict(row) for row in rows]
