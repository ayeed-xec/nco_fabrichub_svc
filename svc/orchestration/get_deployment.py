class GetDeployment:
    def __init__(self, deployment_repo):
        self.deployment_repo = deployment_repo

    def execute(self, deployment_id: str):
        return self.deployment_repo.get(deployment_id)
