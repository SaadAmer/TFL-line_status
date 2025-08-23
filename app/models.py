from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Task(Base):
    """SQLAlchemy ORM model for a scheduled TfL disruption fetch task.

    Attributes:
        id: Auto-incremented primary key.
        schedule_time: The datetime when the task should be executed.
        lines: Comma-separated TfL tube line IDs to query.
        status: Execution status: 'scheduled', 'running', 'completed', or 'failed'.
        result: Raw JSON string returned by TfL (or error message on failure).
    """

    __tablename__ = "tasks"

    id: int = Column(Integer, primary_key=True, index=True)
    schedule_time = Column(DateTime, nullable=False, index=True)
    lines: str = Column(String, nullable=False)
    status: str = Column(String, nullable=False, default="scheduled")
    result: str | None = Column(Text, nullable=True)
