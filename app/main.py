from __future__ import annotations

from fastapi import FastAPI

from app.logging_config import configure_logging
from app.database import init_db
from app.routes import router
from app.scheduler import scheduler


app = FastAPI(
    title="WovenLight TfL Scheduler",
    version="1.0.0",
    description="Schedules TfL Line Disruption queries for specified tube lines.",
)

configure_logging()

app.include_router(router)


@app.on_event("startup")
def on_startup() -> None:
    """Initialize database and start the background scheduler."""
    init_db()
    scheduler.start()


@app.on_event("shutdown")
def on_shutdown() -> None:
    """Gracefully shut down the background scheduler."""
    scheduler.shutdown()
