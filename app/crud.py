from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy.orm import Session

from . import models


def create_task(db: Session, *, schedule_time, lines: str) -> models.Task:
    """Create and persist a new task.

    Args:
        db: SQLAlchemy session.
        schedule_time: Datetime when the task should run.
        lines: Comma-separated tube line IDs.

    Returns:
        Task: The newly created task.
    """
    task = models.Task(schedule_time=schedule_time, lines=lines, status="scheduled")
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_tasks(db: Session) -> list[models.Task]:
    """Return all tasks.

    Args:
        db: SQLAlchemy session.

    Returns:
        list[Task]: List of tasks.
    """
    return list(db.query(models.Task).all())


def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    """Fetch a task by ID.

    Args:
        db: SQLAlchemy session.
        task_id: The task primary key.

    Returns:
        Optional[Task]: The task if found, else None.
    """
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def update_task(
    db: Session,
    task: models.Task,
    *,
    schedule_time=None,
    lines: Optional[str] = None,
) -> models.Task:
    """Update an existing task's schedule time and/or lines.

    Args:
        db: SQLAlchemy session.
        task: Target task instance to update.
        schedule_time: Optional new schedule datetime.
        lines: Optional new comma-separated tube line IDs.

    Returns:
        Task: The updated task instance.
    """
    if schedule_time is not None:
        task.schedule_time = schedule_time
    if lines is not None:
        task.lines = lines
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: models.Task) -> None:
    """Delete a task.

    Args:
        db: SQLAlchemy session.
        task: Task instance to delete.
    """
    db.delete(task)
    db.commit()
