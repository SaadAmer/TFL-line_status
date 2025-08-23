from __future__ import annotations

import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from . import crud, schemas
from .auth import require_auth
from .database import get_db
from .scheduler import schedule_task

router = APIRouter()

# router = APIRouter(dependencies=[Depends(require_auth())])

log = logging.getLogger(__name__)


@router.post("/tasks", response_model=schemas.TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(task_in: schemas.TaskCreate, db: Annotated[Session, Depends(get_db)]) -> schemas.TaskOut:
    """Create a new scheduled TfL disruption task.

    If schedule_time is empty, the task is scheduled to run immediately.

    Args:
        task_in: Payload containing desired schedule time and target lines.
        db: Injected SQLAlchemy session.

    Returns:
        TaskOut: The created task representation.

    Raises:
        HTTPException: If validation fails.
    """
    log.info(
        "create_task: received",
        extra={"path": "/tasks", "method": "POST", "lines": task_in.lines}
    )

    try:
        schedule_time: datetime | None = task_in.normalized_schedule_time()
        if schedule_time is None:
            schedule_time = datetime.now()
        lines: str = task_in.normalized_lines()
    except ValueError as ve:
        log.warning(
            "create_task: invalid input",
            extra={"path": "/tasks", "method": "POST", "error": str(ve)}
        )
        raise HTTPException(status_code=400, detail=str(ve)) from ve

    task = await run_in_threadpool(crud.create_task, db, schedule_time=schedule_time, lines=lines)
    await run_in_threadpool(schedule_task, task)

    log.info(
        "create_task: scheduled",
        extra={"task_id": task.id, "schedule_time": task.schedule_time.isoformat(), "lines": task.lines, "status": task.status}
    )

    return task


@router.get("/tasks", response_model=list[schemas.TaskOut])
async def list_tasks(db: Annotated[Session, Depends(get_db)]) -> list[schemas.TaskOut]:
    """List all tasks.

    Args:
        db: Injected SQLAlchemy session.

    Returns:
        list[TaskOut]: All tasks in the system.
    """
    tasks = await run_in_threadpool(crud.get_tasks, db)
    
    log.info("list_tasks: ok", extra={"count": len(tasks)})

    return tasks


@router.get("/tasks/{task_id}", response_model=schemas.TaskOut)
async def get_task(task_id: int, db: Annotated[Session, Depends(get_db)]) -> schemas.TaskOut:
    """Retrieve a single task by ID.

    Args:
        task_id: Task identifier.
        db: Injected SQLAlchemy session.

    Returns:
        TaskOut: Task representation including current status and result (if any).

    Raises:
        HTTPException: If the task cannot be found.
    """
    task = await run_in_threadpool(crud.get_task, db, task_id)
    if not task:
        log.warning("get_task: not found", extra={"task_id": task_id})
        raise HTTPException(status_code=404, detail="Task not found")
    
    log.info("get_task: ok", extra={"task_id": task_id, "status": task.status})
    return task


@router.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
async def update_task(task_id: int, updates: schemas.TaskUpdate, db: Annotated[Session, Depends(get_db)]) -> schemas.TaskOut:
    """Update an existing task's schedule time and/or lines (only if still scheduled).

    Args:
        task_id: Task identifier.
        updates: Fields to update.
        db: Injected SQLAlchemy session.

    Returns:
        TaskOut: Updated task.

    Raises:
        HTTPException: If task not found or not in 'scheduled' state, or validation fails.
    """
    log.info("update_task: received", extra={"task_id": task_id, "lines": updates.lines})

    task = await run_in_threadpool(crud.get_task, db, task_id)

    if not task:
        log.warning("update_task: not found", extra={"task_id": task_id})
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != "scheduled":
        log.warning("update_task: invalid state", extra={"task_id": task_id, "status": task.status})
        raise HTTPException(status_code=400, detail="Cannot update a running/completed/failed task")

    try:
        new_time = updates.normalized_schedule_time()
        norm_lines = updates.normalized_lines() if hasattr(updates, "normalized_lines") else updates.lines
    except ValueError as ve:
        log.warning("update_task: invalid input", extra={"task_id": task_id, "error": str(ve)})
        raise HTTPException(status_code=400, detail=str(ve)) from ve

    updated = await run_in_threadpool(
        crud.update_task,
        db,
        task,
        schedule_time=new_time if new_time is not None else None,
        lines=norm_lines,
    )

    await run_in_threadpool(schedule_task, updated)

    log.info(
        "update_task: ok",
        extra={"task_id": updated.id, "schedule_time": updated.schedule_time.isoformat(), "lines": updated.lines}
    )

    return updated


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: Annotated[Session, Depends(get_db)]) -> Response:
    """Delete a task by ID.

    Args:
        task_id: Task identifier.
        db: Injected SQLAlchemy session.

    Raises:
        HTTPException: If the task cannot be found.
    """
    log.info("delete_task: received", extra={"task_id": task_id})

    task = await run_in_threadpool(crud.get_task, db, task_id)

    if not task:
        log.warning("delete_task: not found", extra={"task_id": task_id})
        raise HTTPException(status_code=404, detail="Task not found")

    await run_in_threadpool(crud.delete_task, db, task)

    log.info("delete_task: ok", extra={"task_id": task_id})

    return Response(status_code=status.HTTP_204_NO_CONTENT)