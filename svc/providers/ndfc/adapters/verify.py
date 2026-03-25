from svc.providers.ndfc.client import endpoints


class VerifyAdapter:
    def __init__(self, session):
        self.session = session

    def check_jobs(self, deployment_id: str, jobs: list[dict]) -> list[dict]:
        return endpoints.verify_jobs(self.session, deployment_id, jobs)
