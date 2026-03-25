class VerifyDeployment:
    def __init__(self, driver, deployment_repo):
        self.driver = driver
        self.deployment_repo = deployment_repo

    def execute(self, deployment_id: str):
        return self.driver.verify_deployment(deployment_id)
