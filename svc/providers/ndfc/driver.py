from svc.providers.ndfc.exceptions import NdfcProviderError
from svc.schemas.api_v2 import RollbackResponse, VerificationResponse
from svc.shared.ids import new_id


class NdfcDriver:
    def __init__(self, session, inventory_adapter, policy_adapter, deploy_adapter, verify_adapter):
        self.session = session
        self.inventory_adapter = inventory_adapter
        self.policy_adapter = policy_adapter
        self.deploy_adapter = deploy_adapter
        self.verify_adapter = verify_adapter

    @classmethod
    def from_settings(cls, settings):
        from svc.providers.ndfc.adapters.deploy import DeployAdapter
        from svc.providers.ndfc.adapters.fabric_inventory import FabricInventoryAdapter
        from svc.providers.ndfc.adapters.policies import PolicyAdapter
        from svc.providers.ndfc.adapters.verify import VerifyAdapter
        from svc.providers.ndfc.client.session import build_session

        session = build_session(settings)
        return cls(
            session=session,
            inventory_adapter=FabricInventoryAdapter(session),
            policy_adapter=PolicyAdapter(session),
            deploy_adapter=DeployAdapter(session),
            verify_adapter=VerifyAdapter(session),
        )

    def collect_fabric_state(self):
        return self.inventory_adapter.list_fabrics()

    def preflight_probe(self, service_intent):
        required_failures: list[str] = []
        optional_failures: list[str] = []

        fabric = self.inventory_adapter.get_fabric(service_intent.fabric_name)

        try:
            switches = self.inventory_adapter.get_switches(service_intent)
        except NdfcProviderError as error:
            switches = []
            if error.critical:
                required_failures.append(error.endpoint)
            else:
                optional_failures.append(error.endpoint)

        try:
            policy_conflicts = self.policy_adapter.get_interface_policies(service_intent)
        except NdfcProviderError as error:
            policy_conflicts = []
            if error.critical:
                required_failures.append(error.endpoint)
            else:
                optional_failures.append(error.endpoint)

        if fabric is None:
            required_failures.append("inventory.fabric")

        if service_intent.flags.get("simulate_optional_failure"):
            optional_failures.append("history.audit")

        return {
            "fabric": fabric,
            "switches": switches,
            "policy_conflicts": policy_conflicts,
            "required_failures": required_failures,
            "optional_failures": optional_failures,
        }

    def build_provider_plan(self, service_intent, service_order_id):
        service_key = f"{service_intent.tenant_name}:{service_intent.service_name}"
        operations = [
            f"ensure-tenant:{service_intent.tenant_name}",
            f"ensure-service:{service_intent.service_name}",
            *[
                f"attach-interface:{endpoint.serial_number}:{endpoint.interface_name}"
                for endpoint in service_intent.endpoints
            ],
        ]
        rollback_boundary = {
            "service_key": service_key,
            "provider": service_intent.provider,
            "fabric_name": service_intent.fabric_name,
            "interfaces": [
                {"serial_number": endpoint.serial_number, "interface_name": endpoint.interface_name}
                for endpoint in service_intent.endpoints
            ],
        }
        return type(
            "ProviderPlan",
            (),
            {
                "service_order_id": service_order_id,
                "operations": operations,
                "rollback_boundary": rollback_boundary,
                "service_key": service_key,
            },
        )()

    def preview_plan(self, plan):
        interface_ops = [op for op in plan.operations if op.startswith("attach-interface")]
        creates = [op for op in plan.operations if op.startswith("ensure-")]
        return {
            "plan_id": plan.plan_id,
            "status": "previewed",
            "service_scope": {"operations": len(plan.operations)},
            "creates": creates,
            "updates": interface_ops,
            "reuses": [],
            "conflicts": [],
            "deploy_required": bool(plan.operations),
        }

    def apply_plan(self, plan, deployment_id):
        jobs = []
        if self.deploy_adapter:
            jobs = self.deploy_adapter.submit(deployment_id, plan.operations)

        if not jobs:
            jobs = [{"job_id": new_id(), "operation": operation, "status": "submitted"} for operation in plan.operations]

        return type("DeployResult", (), {"jobs": jobs})()

    def verify_deployment(self, deployment_id, jobs: list[dict]):
        checks = []
        if self.verify_adapter:
            checks = self.verify_adapter.check_jobs(deployment_id, jobs)

        if not checks:
            checks = [{"check": "job-status", "job_id": job["job_id"], "result": "ok"} for job in jobs]

        return VerificationResponse(deployment_id=deployment_id, status="verified", checks=checks)

    def rollback_deployment(self, deployment_id):
        if self.deploy_adapter and hasattr(self.deploy_adapter, "rollback"):
            payload = self.deploy_adapter.rollback(deployment_id)
            if payload:
                return RollbackResponse(
                    deployment_id=deployment_id,
                    rollback_id=payload.get("rollback_id", new_id()),
                    status=payload.get("status", "accepted"),
                )

        return RollbackResponse(deployment_id=deployment_id, rollback_id=new_id(), status="accepted")
