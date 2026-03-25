from svc.persistence.repositories.deployments import DeploymentRepository
from svc.persistence.repositories.evidence import EvidenceRepository


def run(deployment_id: str) -> dict[str, object]:
    deployment_repo = DeploymentRepository()
    evidence_repo = EvidenceRepository()

    try:
        deployment = deployment_repo.get(deployment_id)
    except KeyError:
        return {
            "status": "not-found",
            "deployment_id": deployment_id,
            "verification": None,
            "artifacts": [],
        }

    verification = deployment_repo.get_verification(deployment_id)
    artifacts = evidence_repo.list_for_deployment(deployment_id)

    return {
        "status": "ok",
        "deployment": deployment.model_dump(),
        "verification": verification.model_dump(),
        "artifacts": artifacts,
    }
