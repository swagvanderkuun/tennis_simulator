"""
Database session management
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)


def _ensure_elo_current_form_columns() -> None:
    """
    Additive-only safety migration.

    The API uses precomputed form columns on tennis.elo_current; ensure they exist even if
    Dagster hasn't run migrations yet.
    """
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS tennis"))
        conn.execute(text("ALTER TABLE tennis.elo_current ADD COLUMN IF NOT EXISTS elo_4w double precision"))
        conn.execute(text("ALTER TABLE tennis.elo_current ADD COLUMN IF NOT EXISTS elo_12w double precision"))
        conn.execute(text("ALTER TABLE tennis.elo_current ADD COLUMN IF NOT EXISTS form_4w double precision"))
        conn.execute(text("ALTER TABLE tennis.elo_current ADD COLUMN IF NOT EXISTS form_12w double precision"))
        conn.execute(text("ALTER TABLE tennis.elo_current ADD COLUMN IF NOT EXISTS form double precision"))


_ensure_elo_current_form_columns()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


