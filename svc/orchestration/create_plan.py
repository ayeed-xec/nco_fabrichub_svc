from fastapi import HTTPException, status

from svc.domain.rules.validation_rules import build_preflight_response
from svc.schemas.api_v2 import CreatePlanRequest, PlanResponse


class CreatePlan:
    def __init__(self, driver, service_order_repo, plan_repo):
        self.driver = driver
        self.service_order_repo = service_order_repo
        self.plan_repo = plan_repo

    def execute(self, request: CreatePlanRequest) -> PlanResponse:
        preflight = build_preflight_response(
            request.service_intent,
            self.driver.preflight_probe(request.service_intent),
            ownership_records=[],
        )
        if preflight.status != "ready":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": "Plan creation requires a ready preflight decision.",
                    "preflight_status": preflight.status,
                    "conflicts": [conflict.model_dump() for conflict in preflight.conflicts],
                },
            )

        service_order = self.service_order_repo.create_from_request(request)
        plan = self.driver.build_provider_plan(request.service_intent, service_order.service_order_id)
        return self.plan_repo.create(plan)
