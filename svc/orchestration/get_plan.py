class GetPlan:
    def __init__(self, plan_repo):
        self.plan_repo = plan_repo

    def execute(self, plan_id: str):
        return self.plan_repo.get(plan_id)
