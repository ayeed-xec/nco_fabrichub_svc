from svc.providers.ndfc.client import endpoints
from svc.providers.ndfc.exceptions import NdfcProviderError


class PolicyAdapter:
    def __init__(self, session):
        self.session = session

    def get_interface_policies(self, service_intent) -> list[dict]:
        if service_intent.flags.get("simulate_policy_probe_failure"):
            raise NdfcProviderError(
                "Policy endpoint failed",
                endpoint="policies.interfaces",
                critical=True,
            )

        conflicts = endpoints.get_interface_policies(self.session, service_intent.fabric_name)
        if conflicts:
            return conflicts

        derived_conflicts: list[dict] = []
        for endpoint in service_intent.endpoints:
            if endpoint.interface_name.upper().startswith("BAD"):
                derived_conflicts.append(
                    {
                        "serial_number": endpoint.serial_number,
                        "interface_name": endpoint.interface_name,
                    }
                )
        return derived_conflicts
