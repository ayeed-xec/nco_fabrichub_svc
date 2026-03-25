import sqlite3
from contextlib import contextmanager
from pathlib import Path

_DB_PATH = Path(__file__).resolve().parent / "nco_fabrichub.sqlite3"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_schema() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS service_orders (
                service_order_id TEXT PRIMARY KEY,
                provider TEXT NOT NULL,
                fabric_name TEXT NOT NULL,
                tenant_name TEXT NOT NULL,
                service_name TEXT NOT NULL,
                service_type TEXT NOT NULL,
                status TEXT NOT NULL,
                request_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS plans (
                plan_id TEXT PRIMARY KEY,
                service_order_id TEXT NOT NULL,
                plan_hash TEXT NOT NULL,
                status TEXT NOT NULL,
                approval_required INTEGER NOT NULL,
                operations_json TEXT NOT NULL,
                rollback_boundary_json TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS approvals (
                approval_id TEXT PRIMARY KEY,
                plan_id TEXT NOT NULL,
                status TEXT NOT NULL,
                approver TEXT NOT NULL,
                remarks TEXT,
                approved_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS deployments (
                deployment_id TEXT PRIMARY KEY,
                plan_id TEXT NOT NULL,
                status TEXT NOT NULL,
                jobs_json TEXT NOT NULL,
                verification_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS ownership_ledger (
                ownership_id TEXT PRIMARY KEY,
                fabric_name TEXT NOT NULL,
                serial_number TEXT NOT NULL,
                interface_name TEXT NOT NULL,
                owner_service_key TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS evidence_artifacts (
                artifact_id TEXT PRIMARY KEY,
                deployment_id TEXT NOT NULL,
                artifact_type TEXT NOT NULL,
                artifact_path TEXT NOT NULL,
                checksum TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS idempotency_keys (
                idempotency_key TEXT PRIMARY KEY,
                deployment_id TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )


@contextmanager
def get_session():
    initialize_schema()
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
