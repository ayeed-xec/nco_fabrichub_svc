import json
import uuid
from dataclasses import dataclass

from svc.persistence.session import get_session


@dataclass
class ServiceOrderRecord:
    service_order_id: str
    status: str
    provider: str
    fabric_name: str
    tenant_name: str
    service_name: str
    service_type: str


class ServiceOrderRepository:
    def create_from_request(self, request):
        record = ServiceOrderRecord(
            service_order_id=str(uuid.uuid4()),
            status="preflight-ready",
            provider=request.service_intent.provider,
            fabric_name=request.service_intent.fabric_name,
            tenant_name=request.service_intent.tenant_name,
            service_name=request.service_intent.service_name,
            service_type=request.service_intent.service_type,
        )
        with get_session() as conn:
            conn.execute(
                """
                INSERT INTO service_orders (
                    service_order_id, provider, fabric_name, tenant_name, service_name, service_type, status, request_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.service_order_id,
                    record.provider,
                    record.fabric_name,
                    record.tenant_name,
                    record.service_name,
                    record.service_type,
                    record.status,
                    json.dumps(request.model_dump()),
                ),
            )
        return record
