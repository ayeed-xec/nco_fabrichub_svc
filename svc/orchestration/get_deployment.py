class GetDeployment:
    def __init__(self, deployment_repo, evidence_repo):
        self.deployment_repo = deployment_repo
        self.evidence_repo = evidence_repo

    def execute(self, deployment_id: str):
        deployment = self.deployment_repo.get(deployment_id)
        artifacts = self.evidence_repo.list_for_deployment(deployment_id)
        return deployment.model_copy(update={"evidence_refs": [item["artifact_path"] for item in artifacts]})
