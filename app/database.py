from __future__ import annotations

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base

# Prefer Postgres if DATABASE_URL is set, otherwise fall back to local SQLite for dev/tests.
# Examples:
#   postgresql+psycopg2://user:pass@localhost:5432/wovenlight
#   postgresql+psycopg2://user:pass@db:5432/wovenlight   (inside docker-compose)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Postgres
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        future=True,
    )
else:
    # SQLite fallback
    DATABASE_URL = "sqlite:///./tasks.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        future=True,
    )

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Create database tables if they do not exist."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and ensure it is closed."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
