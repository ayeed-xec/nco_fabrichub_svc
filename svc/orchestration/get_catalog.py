class GetCatalog:
    def __init__(self, driver):
        self.driver = driver

    def execute(self):
        fabrics = self.driver.collect_fabric_state()
        return {
            "service_types": ["mgmt-vrf-lite", "data-vrf-lite", "l3-network"],
            "providers": ["cisco-ndfc"],
            "fabrics": fabrics,
            "policy_options": {
                "interface_policy_conflicts": "blocked",
                "preview_mode": "read-only",
            },
        }
