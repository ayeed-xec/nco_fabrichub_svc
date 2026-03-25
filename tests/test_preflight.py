from svc.orchestration.create_preflight import CreatePreflight
from svc.persistence.repositories.ownership import OwnershipRepository
from svc.providers.ndfc.driver import NdfcDriver
from svc.schemas.api_v2 import Endpoint, PreflightRequest, ServiceIntent


class _Driver(NdfcDriver):
    @classmethod
    def build(cls):
        return cls(
            session=None,
            inventory_adapter=type(
                "Inventory",
                (),
                {
                    "get_fabric": lambda _self, name: None if name == "missing-fabric" else {"name": name},
                    "get_switches": lambda _self, intent: [{"serial_number": e.serial_number} for e in intent.endpoints],
                    "list_fabrics": lambda _self: [{"name": "fab-1", "state": "managed"}],
                },
            )(),
            policy_adapter=type(
                "Policy",
                (),
                {
                    "get_interface_policies": lambda _self, intent: [
                        {"serial_number": e.serial_number, "interface_name": e.interface_name}
                        for e in intent.endpoints
                        if e.interface_name.upper().startswith("BAD")
                    ]
                },
            )(),
            deploy_adapter=None,
            verify_adapter=None,
        )


class _DeploymentRepo:
    def __init__(self, has_inflight=False):
        self.has_inflight = has_inflight

    def has_inflight_for_service(self, service_key: str) -> bool:
        return self.has_inflight


def _request(**flags):
    return PreflightRequest(
        service_intent=ServiceIntent(
            fabric_name=flags.pop("fabric_name", "fab-1"),
            tenant_name="tenant-a",
            service_name="svc-a",
            service_type="l3-network",
            endpoints=[Endpoint(serial_number="SER123", interface_name=flags.pop("interface_name", "Eth1/1"), role="edge")],
            flags=flags,
        )
    )


def test_preflight_ready():
    use_case = CreatePreflight(driver=_Driver.build(), ownership_repo=OwnershipRepository())
    response = use_case.execute(_request())
    assert response.status == "ready"
    assert response.decision == "allow"


def test_preflight_blocks_on_missing_fabric():
    use_case = CreatePreflight(driver=_Driver.build(), ownership_repo=OwnershipRepository())
    response = use_case.execute(_request(fabric_name="missing-fabric"))
    assert response.status == "blocked"
    assert any(conflict.code == "MISSING_FABRIC" for conflict in response.conflicts)


def test_preflight_blocks_on_ownership_conflict():
    use_case = CreatePreflight(driver=_Driver.build(), ownership_repo=OwnershipRepository())
    response = use_case.execute(_request(simulate_ownership_conflict=True))
    assert response.status == "blocked"
    assert any(conflict.code == "OWNERSHIP_CONFLICT" for conflict in response.conflicts)


def test_preflight_degraded_on_optional_failure():
    use_case = CreatePreflight(driver=_Driver.build(), ownership_repo=OwnershipRepository())
    response = use_case.execute(_request(simulate_optional_failure=True))
    assert response.status == "degraded"
    assert response.decision == "manual-review"


def test_preflight_blocks_on_policy_conflict():
    use_case = CreatePreflight(driver=_Driver.build(), ownership_repo=OwnershipRepository())
    response = use_case.execute(_request(interface_name="bad-policy"))
    assert response.status == "blocked"
    assert any(conflict.code == "INCOMPATIBLE_INTERFACE_POLICY" for conflict in response.conflicts)


def test_preflight_blocks_on_inflight_deployment_lock():
    use_case = CreatePreflight(
        driver=_Driver.build(),
        ownership_repo=OwnershipRepository(),
        deployment_repo=_DeploymentRepo(has_inflight=True),
    )
    response = use_case.execute(_request())
    assert response.status == "blocked"
    assert any(conflict.code == "INFLIGHT_DEPLOYMENT_LOCK" for conflict in response.conflicts)
