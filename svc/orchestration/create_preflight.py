from svc.domain.rules.validation_rules import build_preflight_response
from svc.schemas.api_v2 import PreflightRequest, PreflightResponse


class _NoopDeploymentRepository:
    def has_inflight_for_service(self, service_key: str) -> bool:
        return False


class CreatePreflight:
    def __init__(self, driver, ownership_repo, deployment_repo=None):
        self.driver = driver
        self.ownership_repo = ownership_repo
        self.deployment_repo = deployment_repo or _NoopDeploymentRepository()

    def execute(self, request: PreflightRequest) -> PreflightResponse:
        fabric_state = self.driver.preflight_probe(request.service_intent)
        ownership = self.ownership_repo.find_for_service_intent(request.service_intent)
        service_key = f"{request.service_intent.tenant_name}:{request.service_intent.service_name}"
        fabric_state["has_inflight_deployment"] = self.deployment_repo.has_inflight_for_service(service_key)
        return build_preflight_response(request.service_intent, fabric_state, ownership)
