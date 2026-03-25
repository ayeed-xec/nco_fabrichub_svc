from svc.core.idempotency import IdempotencyManager
from svc.core.locks import LockManager
from svc.core.settings import get_settings
from svc.orchestration.approve_plan import ApprovePlan
from svc.orchestration.create_plan import CreatePlan
from svc.orchestration.create_preflight import CreatePreflight
from svc.orchestration.deploy_plan import DeployPlan
from svc.orchestration.get_catalog import GetCatalog
from svc.orchestration.get_deployment import GetDeployment
from svc.orchestration.get_plan import GetPlan
from svc.orchestration.get_verification import GetVerification
from svc.orchestration.preview_plan import PreviewPlan
from svc.orchestration.rollback_deployment import RollbackDeployment
from svc.persistence.repositories.approvals import ApprovalRepository
from svc.persistence.repositories.deployments import DeploymentRepository
from svc.persistence.repositories.evidence import EvidenceRepository
from svc.persistence.repositories.idempotency import IdempotencyRepository
from svc.persistence.repositories.ownership import OwnershipRepository
from svc.persistence.repositories.plans import PlanRepository
from svc.persistence.repositories.service_orders import ServiceOrderRepository
from svc.providers.ndfc.driver import NdfcDriver


def _build_driver() -> NdfcDriver:
    settings = get_settings()
    return NdfcDriver.from_settings(settings)


def get_create_preflight_use_case() -> CreatePreflight:
    driver = _build_driver()
    ownership_repo = OwnershipRepository()
    deployment_repo = DeploymentRepository()
    return CreatePreflight(driver=driver, ownership_repo=ownership_repo, deployment_repo=deployment_repo)


def get_create_plan_use_case() -> CreatePlan:
    driver = _build_driver()
    service_order_repo = ServiceOrderRepository()
    plan_repo = PlanRepository()
    return CreatePlan(driver=driver, service_order_repo=service_order_repo, plan_repo=plan_repo)


def get_get_plan_use_case() -> GetPlan:
    return GetPlan(plan_repo=PlanRepository())


def get_preview_plan_use_case() -> PreviewPlan:
    driver = _build_driver()
    plan_repo = PlanRepository()
    return PreviewPlan(driver=driver, plan_repo=plan_repo)


def get_approve_plan_use_case() -> ApprovePlan:
    return ApprovePlan(plan_repo=PlanRepository(), approval_repo=ApprovalRepository())


def get_deploy_plan_use_case() -> DeployPlan:
    driver = _build_driver()
    return DeployPlan(
        driver=driver,
        plan_repo=PlanRepository(),
        deployment_repo=DeploymentRepository(),
        ownership_repo=OwnershipRepository(),
        evidence_repo=EvidenceRepository(),
        lock_manager=LockManager(),
        idempotency_manager=IdempotencyManager(IdempotencyRepository()),
    )


def get_get_deployment_use_case() -> GetDeployment:
    return GetDeployment(deployment_repo=DeploymentRepository())


def get_get_verification_use_case() -> GetVerification:
    return GetVerification(deployment_repo=DeploymentRepository())


def get_rollback_deployment_use_case() -> RollbackDeployment:
    driver = _build_driver()
    return RollbackDeployment(
        driver=driver,
        deployment_repo=DeploymentRepository(),
        plan_repo=PlanRepository(),
    )


def get_catalog_use_case() -> GetCatalog:
    driver = _build_driver()
    return GetCatalog(driver=driver)
