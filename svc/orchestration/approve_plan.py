from fastapi import HTTPException, status


class ApprovePlan:
    def __init__(self, plan_repo, approval_repo):
        self.plan_repo = plan_repo
        self.approval_repo = approval_repo

    def execute(self, plan_id: str, request):
        plan = self.plan_repo.get(plan_id)
        if plan.status not in {"created", "previewed"}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": f"Plan '{plan_id}' is not in an approvable state.", "status": plan.status},
            )
        self.plan_repo.mark_approved(plan_id)
        return self.approval_repo.approve(plan_id=plan_id, approver=request.approver, remarks=request.remarks)
