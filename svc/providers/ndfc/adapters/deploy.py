from svc.providers.ndfc.client import endpoints


class DeployAdapter:
    def __init__(self, session):
        self.session = session

    def submit(self, deployment_id: str, operations: list[str]) -> list[dict]:
        return endpoints.submit_deploy(self.session, deployment_id, operations)

    def rollback(self, deployment_id: str) -> dict:
        return endpoints.submit_rollback(self.session, deployment_id)
