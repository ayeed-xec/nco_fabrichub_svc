from fastapi import APIRouter, Depends, status

from svc.api.dependencies import get_approve_plan_use_case
from svc.orchestration.approve_plan import ApprovePlan
from svc.schemas.api_v2 import ApprovalRequest, ApprovalResponse

router = APIRouter()


@router.post("/plans/{plan_id}/approve", response_model=ApprovalResponse, status_code=status.HTTP_200_OK)
def approve_plan(
    plan_id: str,
    request: ApprovalRequest,
    use_case: ApprovePlan = Depends(get_approve_plan_use_case),
) -> ApprovalResponse:
    return use_case.execute(plan_id, request)
