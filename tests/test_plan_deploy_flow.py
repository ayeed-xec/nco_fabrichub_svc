from fastapi import HTTPException

from svc.core.idempotency import IdempotencyManager
from svc.core.locks import LockManager
from svc.orchestration.approve_plan import ApprovePlan
from svc.orchestration.create_plan import CreatePlan
from svc.orchestration.deploy_plan import DeployPlan
from svc.orchestration.get_deployment import GetDeployment
from svc.orchestration.preview_plan import PreviewPlan
from svc.orchestration.rollback_deployment import RollbackDeployment
from svc.orchestration.verify_deployment import VerifyDeployment
from svc.persistence.repositories.approvals import ApprovalRepository
from svc.persistence.repositories.deployments import DeploymentRepository
from svc.persistence.repositories.evidence import EvidenceRepository
from svc.persistence.repositories.idempotency import IdempotencyRepository
from svc.persistence.repositories.ownership import OwnershipRepository
from svc.persistence.repositories.plans import PlanRepository
from svc.persistence.repositories.service_orders import ServiceOrderRepository
from svc.providers.ndfc.driver import NdfcDriver
from svc.schemas.api_v2 import (
    ApprovalRequest,
    CreatePlanRequest,
    DeployRequest,
    Endpoint,
    ServiceIntent,
)


def _driver() -> NdfcDriver:
    return NdfcDriver(
        session=None,
        inventory_adapter=type(
            "Inventory",
            (),
            {
                "get_fabric": lambda _self, name: {"name": name},
                "get_switches": lambda _self, intent: [{"serial_number": e.serial_number} for e in intent.endpoints],
                "list_fabrics": lambda _self: [{"name": "fab-1", "state": "managed"}],
            },
        )(),
        policy_adapter=type("Policy", (), {"get_interface_policies": lambda _self, _intent: []})(),
        deploy_adapter=None,
        verify_adapter=None,
    )


def _request() -> CreatePlanRequest:
    return CreatePlanRequest(
        service_intent=ServiceIntent(
            fabric_name="fab-1",
            tenant_name="tenant-1",
            service_name="service-1",
            service_type="l3-network",
            endpoints=[Endpoint(serial_number="SER-1", interface_name="Eth1/1", role="edge")],
        )
    )


def _build_deploy_use_case(driver, plan_repo, deployment_repo, ownership_repo, evidence_repo):
    return DeployPlan(
        driver=driver,
        plan_repo=plan_repo,
        deployment_repo=deployment_repo,
        ownership_repo=ownership_repo,
        evidence_repo=evidence_repo,
        lock_manager=LockManager(),
        idempotency_manager=IdempotencyManager(IdempotencyRepository()),
    )


def test_full_plan_approve_deploy_verify_and_rollback_flow():
    driver = _driver()
    plan_repo = PlanRepository()
    deployment_repo = DeploymentRepository()
    ownership_repo = OwnershipRepository()
    evidence_repo = EvidenceRepository()

    create_plan = CreatePlan(driver=driver, service_order_repo=ServiceOrderRepository(), plan_repo=plan_repo)
    preview_plan = PreviewPlan(driver=driver, plan_repo=plan_repo)
    approve_plan = ApprovePlan(plan_repo=plan_repo, approval_repo=ApprovalRepository())
    deploy_plan = _build_deploy_use_case(driver, plan_repo, deployment_repo, ownership_repo, evidence_repo)
    verify_plan = VerifyDeployment(driver=driver, deployment_repo=deployment_repo)
    get_deployment = GetDeployment(deployment_repo=deployment_repo, evidence_repo=evidence_repo)
    rollback = RollbackDeployment(driver=driver, deployment_repo=deployment_repo, plan_repo=plan_repo)

    plan = create_plan.execute(_request())
    preview = preview_plan.execute(plan.plan_id)
    assert preview.deploy_required is True
    assert plan_repo.get(plan.plan_id).status == "previewed"

    approval = approve_plan.execute(plan.plan_id, ApprovalRequest(approver="approver-a"))
    assert approval.status == "approved"

    deployment = deploy_plan.execute(plan.plan_id, DeployRequest(actor="actor-a", idempotency_key="idem-1"))
    assert deployment.status == "completed"
    assert plan_repo.get(plan.plan_id).status == "deployed"

    verification = verify_plan.execute(deployment.deployment_id)
    assert verification.status == "verified"

    hydrated = get_deployment.execute(deployment.deployment_id)
    assert len(hydrated.evidence_refs) == 1

    ownership_conflicts = ownership_repo.find_for_service_intent(_request().service_intent)
    assert ownership_conflicts == []

    rollback_result = rollback.execute(deployment.deployment_id)
    assert rollback_result.status == "accepted"
    assert deployment_repo.get(deployment.deployment_id).status == "rolled_back"
    assert plan_repo.get(plan.plan_id).status == "rolled_back"


def test_deploy_requires_approval():
    driver = _driver()
    plan_repo = PlanRepository()
    deployment_repo = DeploymentRepository()

    plan = CreatePlan(driver=driver, service_order_repo=ServiceOrderRepository(), plan_repo=plan_repo).execute(_request())
    deploy_plan = _build_deploy_use_case(driver, plan_repo, deployment_repo, OwnershipRepository(), EvidenceRepository())

    try:
        deploy_plan.execute(plan.plan_id, DeployRequest(actor="actor-a"))
    except HTTPException as error:
        assert error.status_code == 409
        return
    raise AssertionError("Expected deploy to fail without approval")


def test_deploy_uses_idempotency_key_to_return_existing_deployment():
    driver = _driver()
    plan_repo = PlanRepository()
    deployment_repo = DeploymentRepository()
    ownership_repo = OwnershipRepository()
    evidence_repo = EvidenceRepository()

    create_plan = CreatePlan(driver=driver, service_order_repo=ServiceOrderRepository(), plan_repo=plan_repo)
    approve_plan = ApprovePlan(plan_repo=plan_repo, approval_repo=ApprovalRepository())
    deploy_plan = _build_deploy_use_case(driver, plan_repo, deployment_repo, ownership_repo, evidence_repo)

    plan = create_plan.execute(_request())
    approve_plan.execute(plan.plan_id, ApprovalRequest(approver="approver-a"))

    first = deploy_plan.execute(plan.plan_id, DeployRequest(actor="actor-a", idempotency_key="same-key"))
    second = deploy_plan.execute(plan.plan_id, DeployRequest(actor="actor-a", idempotency_key="same-key"))

    assert first.deployment_id == second.deployment_id


def test_rollback_blocked_when_newer_completed_deployment_exists():
    driver = _driver()
    plan_repo = PlanRepository()
    deployment_repo = DeploymentRepository()
    ownership_repo = OwnershipRepository()
    evidence_repo = EvidenceRepository()

    create_plan = CreatePlan(driver=driver, service_order_repo=ServiceOrderRepository(), plan_repo=plan_repo)
    approve_plan = ApprovePlan(plan_repo=plan_repo, approval_repo=ApprovalRepository())
    deploy_plan = _build_deploy_use_case(driver, plan_repo, deployment_repo, ownership_repo, evidence_repo)
    rollback = RollbackDeployment(driver=driver, deployment_repo=deployment_repo, plan_repo=plan_repo)

    plan = create_plan.execute(_request())
    approve_plan.execute(plan.plan_id, ApprovalRequest(approver="approver-a"))
    first = deploy_plan.execute(plan.plan_id, DeployRequest(actor="actor-a", idempotency_key="old-key"))
    second = deploy_plan.execute(plan.plan_id, DeployRequest(actor="actor-a", idempotency_key="new-key"))

    assert first.deployment_id != second.deployment_id

    try:
        rollback.execute(first.deployment_id)
    except HTTPException as error:
        assert error.status_code == 409
        assert "newer completed deployment" in error.detail["message"]
        return
    raise AssertionError("Expected rollback to be blocked for older deployment")


def test_verify_requires_completed_or_rolled_back_deployment():
    driver = _driver()
    deployment_repo = DeploymentRepository()
    verify = VerifyDeployment(driver=driver, deployment_repo=deployment_repo)

    pending = deployment_repo.create_pending(plan_id="plan-x", actor="actor-a")

    try:
        verify.execute(pending.deployment_id)
    except HTTPException as error:
        assert error.status_code == 409
        return
    raise AssertionError("Expected verify to be blocked for pending deployment")
