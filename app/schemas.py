from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# Tube (Underground) line IDs (11) – the exercise scope excludes DLR/Overground/etc.
VALID_TUBE_LINES: set[str] = {
    "bakerloo",
    "central",
    "circle",
    "district",
    "hammersmith-city",
    "jubilee",
    "metropolitan",
    "northern",
    "piccadilly",
    "victoria",
    "waterloo-city",
}


class TaskCreate(BaseModel):
    """Input model for creating a task."""

    schedule_time: Optional[datetime] = Field(default=None, alias="schedule_time")
    scheduler_time: Optional[datetime] = Field(default=None, alias="scheduler_time")
    lines: str = Field(..., description="Comma-separated TfL tube line IDs.")

    model_config = ConfigDict(populate_by_name=True)

    def normalized_schedule_time(self) -> Optional[datetime]:
        """Return the provided schedule time, resolving the alias if used.

        Returns:
            Optional[datetime]: The parsed schedule time or None if missing.
        """
        dt = self.schedule_time or self.scheduler_time
        if dt is None:
            return None
        # normalize to seconds to match '%Y-%m-%dT%H:%M:%S' spirit
        return dt.replace(microsecond=0)

    def normalized_lines(self) -> str:
        """Return normalized, comma-separated, validated tube line IDs.

        Raises:
            ValueError: If any provided line ID is invalid.

        Returns:
            str: Normalized comma-separated line IDs.
        """
        items: list[str] = [s.strip().lower() for s in self.lines.split(",") if s.strip()]
        invalid: list[str] = [x for x in items if x not in VALID_TUBE_LINES]
        if invalid:
            raise ValueError(
                f"Invalid line id(s): {', '.join(invalid)}. "
                f"Valid tube lines: {', '.join(sorted(VALID_TUBE_LINES))}"
            )
        return ",".join(items)


class TaskUpdate(BaseModel):
    """Input model for updating an existing task (only if still scheduled)."""

    schedule_time: Optional[datetime] = None
    scheduler_time: Optional[datetime] = Field(default=None, alias="scheduler_time")
    lines: Optional[str] = Field(default=None, description="Comma-separated TfL tube line IDs.")

    model_config = ConfigDict(populate_by_name=True)

    def normalized_schedule_time(self) -> Optional[datetime]:
        """Return provided schedule time (from either field) normalized to seconds."""
        dt = self.schedule_time if self.schedule_time is not None else self.scheduler_time
        return dt.replace(microsecond=0) if dt is not None else None

    def normalized_lines(self) -> Optional[str]:
        """Validate and normalize provided lines if present.

        Raises:
            ValueError: If any provided line ID is invalid.

        Returns:
            Optional[str]: Normalized comma-separated line IDs, or None if missing.
        """
        if self.lines is None:
            return None
        items: list[str] = [s.strip().lower() for s in self.lines.split(",") if s.strip()]
        invalid: list[str] = [x for x in items if x not in VALID_TUBE_LINES]
        if invalid:
            raise ValueError(
                f"Invalid line id(s): {', '.join(invalid)}. "
                f"Valid tube lines: {', '.join(sorted(VALID_TUBE_LINES))}"
            )
        return ",".join(items)


class TaskOut(BaseModel):
    """Public representation of a task."""

    id: int
    schedule_time: datetime
    lines: str
    status: str
    result: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
