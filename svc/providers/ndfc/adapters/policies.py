class PolicyAdapter:
    def __init__(self, session):
        self.session = session

    def get_interface_policies(self, service_intent) -> list[dict]:
        conflicts: list[dict] = []
        for endpoint in service_intent.endpoints:
            if endpoint.interface_name.upper().startswith("BAD"):
                conflicts.append(
                    {
                        "serial_number": endpoint.serial_number,
                        "interface_name": endpoint.interface_name,
                    }
                )
        return conflicts
