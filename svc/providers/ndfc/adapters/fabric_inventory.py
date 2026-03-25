class FabricInventoryAdapter:
    def __init__(self, session):
        self.session = session

    def get_fabric(self, fabric_name: str) -> dict | None:
        if fabric_name == "missing-fabric":
            return None
        return {"name": fabric_name}

    def get_switches(self, service_intent) -> list[dict]:
        return [{"serial_number": endpoint.serial_number} for endpoint in service_intent.endpoints]

    def list_fabrics(self) -> list[dict]:
        return [
            {"name": "fab-1", "state": "managed"},
            {"name": "fab-2", "state": "managed"},
        ]
