from fastapi import APIRouter, Depends, status

from svc.api.dependencies import (
    get_create_plan_use_case,
    get_get_plan_use_case,
    get_preview_plan_use_case,
)
from svc.orchestration.create_plan import CreatePlan
from svc.orchestration.get_plan import GetPlan
from svc.orchestration.preview_plan import PreviewPlan
from svc.schemas.api_v2 import CreatePlanRequest, PlanResponse, PreviewResponse

router = APIRouter()


@router.post("/plans", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(
    request: CreatePlanRequest,
    use_case: CreatePlan = Depends(get_create_plan_use_case),
) -> PlanResponse:
    return use_case.execute(request)


@router.get("/plans/{plan_id}", response_model=PlanResponse)
def get_plan(
    plan_id: str,
    use_case: GetPlan = Depends(get_get_plan_use_case),
) -> PlanResponse:
    return use_case.execute(plan_id)


@router.post("/plans/{plan_id}/preview", response_model=PreviewResponse)
def preview_plan(
    plan_id: str,
    use_case: PreviewPlan = Depends(get_preview_plan_use_case),
) -> PreviewResponse:
    return use_case.execute(plan_id)
