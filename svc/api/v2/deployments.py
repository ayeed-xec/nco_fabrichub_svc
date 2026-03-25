from fastapi import APIRouter, Depends, status

from svc.api.dependencies import (
    get_deploy_plan_use_case,
    get_get_deployment_use_case,
    get_get_verification_use_case,
    get_rollback_deployment_use_case,
    get_verify_deployment_use_case,
)
from svc.orchestration.deploy_plan import DeployPlan
from svc.orchestration.get_deployment import GetDeployment
from svc.orchestration.get_verification import GetVerification
from svc.orchestration.rollback_deployment import RollbackDeployment
from svc.orchestration.verify_deployment import VerifyDeployment
from svc.schemas.api_v2 import (
    DeployRequest,
    DeploymentResponse,
    RollbackResponse,
    VerificationResponse,
)

router = APIRouter()


@router.post("/plans/{plan_id}/deploy", response_model=DeploymentResponse, status_code=status.HTTP_202_ACCEPTED)
def deploy_plan(
    plan_id: str,
    request: DeployRequest,
    use_case: DeployPlan = Depends(get_deploy_plan_use_case),
) -> DeploymentResponse:
    return use_case.execute(plan_id, request)


@router.get("/deployments/{deployment_id}", response_model=DeploymentResponse)
def get_deployment(
    deployment_id: str,
    use_case: GetDeployment = Depends(get_get_deployment_use_case),
) -> DeploymentResponse:
    return use_case.execute(deployment_id)


@router.get("/deployments/{deployment_id}/verification", response_model=VerificationResponse)
def get_verification(
    deployment_id: str,
    use_case: GetVerification = Depends(get_get_verification_use_case),
) -> VerificationResponse:
    return use_case.execute(deployment_id)


@router.post("/deployments/{deployment_id}/verify", response_model=VerificationResponse)
def verify_deployment(
    deployment_id: str,
    use_case: VerifyDeployment = Depends(get_verify_deployment_use_case),
) -> VerificationResponse:
    return use_case.execute(deployment_id)


@router.post(
    "/deployments/{deployment_id}/rollback",
    response_model=RollbackResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def rollback_deployment(
    deployment_id: str,
    use_case: RollbackDeployment = Depends(get_rollback_deployment_use_case),
) -> RollbackResponse:
    return use_case.execute(deployment_id)
