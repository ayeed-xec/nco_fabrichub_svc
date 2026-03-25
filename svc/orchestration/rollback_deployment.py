from fastapi import HTTPException, status


class RollbackDeployment:
    def __init__(self, driver, deployment_repo, plan_repo):
        self.driver = driver
        self.deployment_repo = deployment_repo
        self.plan_repo = plan_repo

    def execute(self, deployment_id: str):
        deployment = self.deployment_repo.get(deployment_id)
        if deployment.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": "Rollback is only allowed for completed deployments."},
            )

        if self.deployment_repo.has_newer_completed_deployment(deployment.plan_id, deployment_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": "Rollback denied because a newer completed deployment exists."},
            )

        plan = self.plan_repo.get(deployment.plan_id)
        if not plan.rollback_boundary.get("interfaces"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": "Rollback boundary is missing interface scope."},
            )

        result = self.driver.rollback_deployment(deployment_id)
        self.deployment_repo.mark_rolled_back(deployment_id)
        self.plan_repo.mark_rolled_back(plan.plan_id)
        return result
