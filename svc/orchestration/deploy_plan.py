from fastapi import HTTPException, status

from svc.core.idempotency import IdempotencyManager
from svc.core.locks import LockManager, LockUnavailableError
from svc.persistence.repositories.idempotency import IdempotencyRepository


class DeployPlan:
    def __init__(
        self,
        driver,
        plan_repo,
        deployment_repo,
        ownership_repo,
        evidence_repo,
        lock_manager: LockManager | None = None,
        idempotency_manager: IdempotencyManager | None = None,
    ):
        self.driver = driver
        self.plan_repo = plan_repo
        self.deployment_repo = deployment_repo
        self.ownership_repo = ownership_repo
        self.evidence_repo = evidence_repo
        self.lock_manager = lock_manager or LockManager()
        self.idempotency_manager = idempotency_manager or IdempotencyManager(IdempotencyRepository())

    def execute(self, plan_id: str, request):
        plan = self.plan_repo.get(plan_id)
        if plan.status != "approved":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": "Plan must be approved before deployment.", "status": plan.status},
            )

        existing = self.idempotency_manager.get_existing_deployment(request.idempotency_key)
        if existing:
            return self.deployment_repo.get(existing)

        lock_key = plan.rollback_boundary.get("service_key", plan.plan_id)
        try:
            with self.lock_manager.acquire(lock_key):
                deployment = self.deployment_repo.create_pending(plan_id=plan.plan_id, actor=request.actor)
                result = self.driver.apply_plan(plan, deployment.deployment_id)
                self.deployment_repo.mark_started(deployment.deployment_id, result.jobs)

                verification = self.driver.verify_deployment(deployment.deployment_id, result.jobs)
                self.deployment_repo.save_verification(verification)
                self.deployment_repo.mark_completed(deployment.deployment_id, result.jobs)

                self.ownership_repo.claim_from_plan(plan)
                self.evidence_repo.add_artifact(
                    deployment_id=deployment.deployment_id,
                    artifact_type="verification",
                    artifact_path=f"evidence/{deployment.deployment_id}/verification.json",
                    checksum=f"checks:{len(verification.checks)}",
                )
                self.plan_repo.mark_deployed(plan.plan_id)
                self.idempotency_manager.save_result(request.idempotency_key, deployment.deployment_id)
                return self.deployment_repo.get(deployment.deployment_id)
        except LockUnavailableError as error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": "Another deployment is in progress for this service scope."},
            ) from error
