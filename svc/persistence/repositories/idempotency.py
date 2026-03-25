from svc.persistence.session import get_session


class IdempotencyRepository:
    def get(self, key: str) -> str | None:
        with get_session() as conn:
            row = conn.execute("SELECT deployment_id FROM idempotency_keys WHERE idempotency_key = ?", (key,)).fetchone()
        return row["deployment_id"] if row else None

    def save(self, key: str, deployment_id: str) -> None:
        with get_session() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO idempotency_keys (idempotency_key, deployment_id) VALUES (?, ?)",
                (key, deployment_id),
            )
