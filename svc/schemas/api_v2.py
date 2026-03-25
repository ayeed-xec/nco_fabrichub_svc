from typing import Any, Literal

from pydantic import BaseModel, Field


class Endpoint(BaseModel):
    device_ref: str | None = None
    serial_number: str
    interface_name: str
    role: str
    description: str | None = None
    p2p_subnet: str | None = None


class RoutingIntent(BaseModel):
    local_asn: int | None = None
    peer_asn: int | None = None
    route_target: str | None = None


class Layer3Intent(BaseModel):
    vrf_id: int | None = None
    vlan_id: int | None = None
    gateway_subnet: str | None = None


class ServiceIntent(BaseModel):
    provider: Literal["cisco-ndfc"] = "cisco-ndfc"
    fabric_name: str
    tenant_name: str
    service_name: str
    service_type: Literal["mgmt-vrf-lite", "data-vrf-lite", "l3-network"]
    endpoints: list[Endpoint]
    routing: RoutingIntent | None = None
    layer3: Layer3Intent | None = None
    qos: dict[str, Any] = Field(default_factory=dict)
    flags: dict[str, Any] = Field(default_factory=dict)


class PreflightRequest(BaseModel):
    service_intent: ServiceIntent


class ConflictItem(BaseModel):
    code: str
    severity: Literal["error", "warning"]
    message: str
    context: dict[str, Any] = Field(default_factory=dict)


class FabricHealth(BaseModel):
    status: Literal["healthy", "degraded", "unreachable"]
    failed_endpoints: list[str] = Field(default_factory=list)


class ResourcePlan(BaseModel):
    vrf_id: int | None = None
    vlan_id: int | None = None


class PreflightResponse(BaseModel):
    request_id: str
    status: Literal["ready", "blocked", "degraded"]
    decision: Literal["allow", "deny", "manual-review"]
    fabric_health: FabricHealth
    conflicts: list[ConflictItem] = Field(default_factory=list)
    resource_plan: ResourcePlan = Field(default_factory=ResourcePlan)


class CreatePlanRequest(BaseModel):
    service_intent: ServiceIntent


class PlanResponse(BaseModel):
    plan_id: str
    plan_hash: str
    status: str
    approval_required: bool
    operations: list[str] = Field(default_factory=list)
    rollback_boundary: dict[str, Any] = Field(default_factory=dict)


class PreviewResponse(BaseModel):
    plan_id: str
    status: str
    service_scope: dict[str, Any] = Field(default_factory=dict)
    creates: list[str] = Field(default_factory=list)
    updates: list[str] = Field(default_factory=list)
    reuses: list[str] = Field(default_factory=list)
    conflicts: list[ConflictItem] = Field(default_factory=list)
    deploy_required: bool = True


class ApprovalRequest(BaseModel):
    approver: str
    remarks: str | None = None


class ApprovalResponse(BaseModel):
    approval_id: str
    plan_id: str
    status: str


class DeployRequest(BaseModel):
    actor: str
    idempotency_key: str | None = None


class DeploymentResponse(BaseModel):
    deployment_id: str
    plan_id: str
    status: str
    jobs: list[dict[str, Any]] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


class VerificationResponse(BaseModel):
    deployment_id: str
    status: str
    checks: list[dict[str, Any]] = Field(default_factory=list)


class RollbackResponse(BaseModel):
    deployment_id: str
    rollback_id: str
    status: str
