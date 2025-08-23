from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./tasks.db"

# check_same_thread=False is required for SQLite with multi-threaded app servers
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Create database tables if they do not exist."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and ensure it is closed.

    Yields:
        Session: SQLAlchemy session bound to the engine.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
