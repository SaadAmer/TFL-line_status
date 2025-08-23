from __future__ import annotations

from datetime import datetime
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from sqlalchemy.orm import Session

from .crud import get_task
from .database import SessionLocal
from .models import Task
from .tfl_client import fetch_disruptions

scheduler = BackgroundScheduler()


def run_task(task_id: int) -> None:
    """Execute the scheduled TfL fetch for a given task ID.

    This transitions the task through statuses: 'running' → ('completed'|'failed').

    Args:
        task_id: Identifier of the task to run.
    """
    db: Session = SessionLocal()
    try:
        task: Optional[Task] = get_task(db, task_id)
        if task is None:
            return

        task.status = "running"
        db.commit()

        try:
            task.result = fetch_disruptions(task.lines)
            task.status = "completed"
        except Exception as exc:  # noqa: BLE001
            task.result = f"{type(exc).__name__}: {exc}"
            task.status = "failed"
        finally:
            db.commit()
    finally:
        db.close()


def schedule_task(task: Task) -> None:
    """Schedule or reschedule a task to run at its `schedule_time`.

    Removes a prior job with the same ID (if any) to avoid duplicates.

    Args:
        task: The task instance to schedule.
    """
    job_id = str(task.id)
    try:
        scheduler.remove_job(job_id)
    except Exception:
        pass

    trigger = DateTrigger(run_date=task.schedule_time)
    scheduler.add_job(run_task, trigger, args=[task.id], id=job_id, misfire_grace_time=None)
