from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """
    Create an isolated TestClient per test:
    - point DATABASE_URL at a fresh sqlite file under tmp_path
    - disable the background scheduler
    - import app AFTER env is set, then init_db()
    - return a context-managed TestClient so startup/shutdown run
    """
    db_path = tmp_path / "test_tasks.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    monkeypatch.setenv("DISABLE_SCHEDULER", "1")

    from app.database import init_db
    from app.main import app

    init_db()

    with TestClient(app) as c:
        yield c
