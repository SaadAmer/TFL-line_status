from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import json
import pytest

from app.database import SessionLocal
from app.scheduler import run_task
from app import crud, models


def test_create_task_immediate(client) -> None:
    """
    GIVEN a request to create a task without providing a schedule time
    WHEN the client posts a task with only the line "victoria"
    THEN the service should create a task scheduled immediately,
         returning status 201 and a response with "scheduled" status.
    """
    resp = client.post("/tasks", json={"lines": "victoria"})
    assert resp.status_code == 201, resp.text
    data: dict[str, Any] = resp.json()
    assert data["lines"] == "victoria"
    assert data["status"] == "scheduled"
    assert isinstance(data["id"], int)


def test_create_task_with_alias_key_scheduler_time(client) -> None:
    """
    GIVEN a request with the alias key `scheduler_time`
    WHEN the client posts a task with a valid future datetime and "central" line
    THEN the service should accept the alias, schedule the task at that time,
         and return the created task with matching schedule_time and lines.
    """
    run_at = (datetime.now() + timedelta(minutes=5)).replace(microsecond=0).isoformat()
    resp = client.post("/tasks", json={"scheduler_time": run_at, "lines": "central"})
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["lines"] == "central"
    assert data["schedule_time"].startswith(run_at[:16])


def test_create_task_invalid_line(client) -> None:
    """
    GIVEN an invalid tube line identifier
    WHEN the client posts a task with "notaline"
    THEN the service should reject the request with HTTP 400
         and return a message indicating invalid line id(s).
    """
    resp = client.post("/tasks", json={"lines": "notaline"})
    assert resp.status_code == 400
    assert "Invalid line id" in resp.json()["detail"]


def test_list_tasks(client) -> None:
    """
    GIVEN existing tasks in the system
    WHEN the client requests the list of all tasks
    THEN the service should return HTTP 200 with a JSON array of tasks.
    """
    resp = client.get("/tasks")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_update_only_when_scheduled(client) -> None:
    """
    GIVEN a task that is still in 'scheduled' state
    WHEN the client sends a PATCH request to update its lines
    THEN the service should update successfully and return the new lines.

    GIVEN a task that is already running/completed/failed
    WHEN the client attempts to update it
    THEN the service should reject with HTTP 400 (not covered here).
    """
    run_at = (datetime.now() + timedelta(hours=1)).replace(microsecond=0).isoformat()
    create = client.post("/tasks", json={"scheduler_time": run_at, "lines": "victoria"})
    assert create.status_code == 201
    task_id = create.json()["id"]

    patch = client.patch(f"/tasks/{task_id}", json={"lines": "victoria,central"})
    assert patch.status_code == 200
    assert patch.json()["lines"] == "victoria,central"


def test_delete_task(client) -> None:
    """
    GIVEN a successfully created task
    WHEN the client deletes the task by ID
    THEN the service should return HTTP 204,
         and subsequent GET requests for that ID should return 404.
    """
    resp = client.post("/tasks", json={"lines": "bakerloo"})
    assert resp.status_code == 201
    task_id = resp.json()["id"]

    del_resp = client.delete(f"/tasks/{task_id}")
    assert del_resp.status_code == 204

    get_resp = client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 404


def test_task_status_transitions_when_job_runs(client, monkeypatch) -> None:
    """
    GIVEN a scheduled task
    WHEN the scheduler's job runner is invoked
    THEN the task moves to 'completed' and result is populated.
    """
    from app import tfl_client
    monkeypatch.setattr(tfl_client, "fetch_disruptions", lambda lines: json.dumps([{"ok": True, "lines": lines}]))

    resp = client.post("/tasks", json={"lines": "victoria"})
    assert resp.status_code == 201
    task_id = resp.json()["id"]

    run_task(task_id)

    check = client.get(f"/tasks/{task_id}")
    assert check.status_code == 200
    data: dict[str, Any] = check.json()
    assert data["status"] == "completed"
    assert data["result"]