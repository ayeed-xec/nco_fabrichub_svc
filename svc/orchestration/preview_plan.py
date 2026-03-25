from svc.schemas.api_v2 import PreviewResponse


class PreviewPlan:
    def __init__(self, driver, plan_repo):
        self.driver = driver
        self.plan_repo = plan_repo

    def execute(self, plan_id: str) -> PreviewResponse:
        plan = self.plan_repo.get(plan_id)
        preview = PreviewResponse(**self.driver.preview_plan(plan))
        self.plan_repo.mark_previewed(plan_id)
        return preview
