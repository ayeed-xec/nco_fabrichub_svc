from svc.persistence.repositories.idempotency import IdempotencyRepository


class IdempotencyManager:
    def __init__(self, repository: IdempotencyRepository):
        self.repository = repository

    def get_existing_deployment(self, key: str | None) -> str | None:
        if not key:
            return None
        return self.repository.get(key)

    def save_result(self, key: str | None, deployment_id: str) -> None:
        if not key:
            return
        self.repository.save(key, deployment_id)
