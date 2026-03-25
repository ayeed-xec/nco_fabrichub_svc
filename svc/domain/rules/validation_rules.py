from svc.schemas.api_v2 import ConflictItem, FabricHealth, PreflightResponse, ResourcePlan
from svc.shared.ids import new_id


def build_preflight_response(service_intent, fabric_state: dict, ownership_records: list[dict]) -> PreflightResponse:
    blockers: list[ConflictItem] = []
    warnings: list[ConflictItem] = []

    required_failures = fabric_state.get("required_failures", [])
    optional_failures = fabric_state.get("optional_failures", [])

    if fabric_state.get("fabric") is None:
        blockers.append(
            ConflictItem(
                code="MISSING_FABRIC",
                severity="error",
                message=f"Fabric '{service_intent.fabric_name}' was not found in NDFC.",
            )
        )

    if fabric_state.get("has_inflight_deployment"):
        blockers.append(
            ConflictItem(
                code="INFLIGHT_DEPLOYMENT_LOCK",
                severity="error",
                message="Another deployment is currently active for this service scope.",
            )
        )

    discovered_switches = {
        switch.get("serial_number") for switch in fabric_state.get("switches", []) if switch.get("serial_number")
    }
    for endpoint in service_intent.endpoints:
        if endpoint.serial_number not in discovered_switches:
            blockers.append(
                ConflictItem(
                    code="MISSING_SWITCH",
                    severity="error",
                    message=f"Switch '{endpoint.serial_number}' was not discovered in fabric inventory.",
                    context={"serial_number": endpoint.serial_number},
                )
            )
        if not endpoint.interface_name:
            blockers.append(
                ConflictItem(
                    code="UNRESOLVED_INTERFACE",
                    severity="error",
                    message="Endpoint interface_name is required.",
                    context={"serial_number": endpoint.serial_number},
                )
            )

    for record in ownership_records:
        if record.get("owner_service_key") != f"{service_intent.tenant_name}:{service_intent.service_name}":
            blockers.append(
                ConflictItem(
                    code="OWNERSHIP_CONFLICT",
                    severity="error",
                    message="Requested object is owned by another service.",
                    context=record,
                )
            )

    for policy_conflict in fabric_state.get("policy_conflicts", []):
        blockers.append(
            ConflictItem(
                code="INCOMPATIBLE_INTERFACE_POLICY",
                severity="error",
                message="Existing interface policy is incompatible with requested service.",
                context=policy_conflict,
            )
        )

    for failed_endpoint in required_failures:
        blockers.append(
            ConflictItem(
                code="CONTROLLER_UNCERTAINTY",
                severity="error",
                message="Required NDFC endpoint failed during preflight.",
                context={"endpoint": failed_endpoint},
            )
        )

    for failed_endpoint in optional_failures:
        warnings.append(
            ConflictItem(
                code="OBSERVABILITY_GAP",
                severity="warning",
                message="Optional NDFC endpoint failed; preflight degraded.",
                context={"endpoint": failed_endpoint},
            )
        )

    if blockers:
        status = "blocked"
        decision = "deny"
    elif warnings:
        status = "degraded"
        decision = "manual-review"
    else:
        status = "ready"
        decision = "allow"

    if required_failures:
        health_status = "unreachable"
    elif optional_failures:
        health_status = "degraded"
    else:
        health_status = "healthy"

    return PreflightResponse(
        request_id=new_id(),
        status=status,
        decision=decision,
        fabric_health=FabricHealth(status=health_status, failed_endpoints=[*required_failures, *optional_failures]),
        conflicts=[*blockers, *warnings],
        resource_plan=ResourcePlan(
            vrf_id=service_intent.layer3.vrf_id if service_intent.layer3 else None,
            vlan_id=service_intent.layer3.vlan_id if service_intent.layer3 else None,
        ),
    )
