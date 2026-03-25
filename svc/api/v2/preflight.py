from fastapi import APIRouter, Depends, status

from svc.api.dependencies import get_create_preflight_use_case
from svc.orchestration.create_preflight import CreatePreflight
from svc.schemas.api_v2 import PreflightRequest, PreflightResponse

router = APIRouter()


@router.post("/preflight", response_model=PreflightResponse, status_code=status.HTTP_200_OK)
def create_preflight(
    request: PreflightRequest,
    use_case: CreatePreflight = Depends(get_create_preflight_use_case),
) -> PreflightResponse:
    return use_case.execute(request)
