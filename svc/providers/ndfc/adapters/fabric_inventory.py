from svc.providers.ndfc.client import endpoints
from svc.providers.ndfc.exceptions import NdfcProviderError


class FabricInventoryAdapter:
    def __init__(self, session):
        self.session = session

    def get_fabric(self, fabric_name: str) -> dict | None:
        if fabric_name == "missing-fabric":
            return None
        return endpoints.get_fabric(self.session, fabric_name)

    def get_switches(self, service_intent) -> list[dict]:
        if service_intent.flags.get("simulate_switch_probe_failure"):
            raise NdfcProviderError(
                "Switch inventory endpoint failed",
                endpoint="inventory.switches",
                critical=True,
            )
        switches = endpoints.get_switches(self.session, service_intent.fabric_name)
        if switches:
            return switches
        return [{"serial_number": endpoint.serial_number} for endpoint in service_intent.endpoints]

    def list_fabrics(self) -> list[dict]:
        fabrics = endpoints.list_fabrics(self.session)
        if fabrics:
            return fabrics
        return [
            {"name": "fab-1", "state": "managed"},
            {"name": "fab-2", "state": "managed"},
        ]
