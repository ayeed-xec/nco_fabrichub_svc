from pathlib import Path

import pytest

DB_PATH = Path(__file__).resolve().parents[1] / "svc" / "persistence" / "nco_fabrichub.sqlite3"


@pytest.fixture(autouse=True)
def reset_sqlite_db():
    if DB_PATH.exists():
        DB_PATH.unlink()
    yield
    if DB_PATH.exists():
        DB_PATH.unlink()
