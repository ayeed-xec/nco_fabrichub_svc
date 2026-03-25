from fastapi import HTTPException, status


class VerifyDeployment:
    def __init__(self, driver, deployment_repo):
        self.driver = driver
        self.deployment_repo = deployment_repo

    def execute(self, deployment_id: str):
        deployment = self.deployment_repo.get(deployment_id)
        if deployment.status not in {"completed", "rolled_back"}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": "Verification requires a completed or rolled back deployment."},
            )

        verification = self.driver.verify_deployment(deployment_id, deployment.jobs)
        self.deployment_repo.save_verification(verification)
        return verification
