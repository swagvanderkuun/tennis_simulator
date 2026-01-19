from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def _try_build_db_url_from_tennis_dagster_env() -> str | None:
    """
    Convenience: if you run the Streamlit dashboard on the host, it can connect to the
    tennis_dagster Postgres exposed on localhost:<POSTGRES_PORT>. We try to read that
    from infra/tennis_dagster/tennis_dagster.env if present.
    """
    env_path = Path("infra/tennis_dagster/tennis_dagster.env")
    if not env_path.exists():
        return None
    values: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        values[k.strip()] = v.strip().strip('"')

    user = values.get("POSTGRES_USER", "tennis")
    password = values.get("POSTGRES_PASSWORD", "tennis")
    db = values.get("POSTGRES_DB", "tennis_simulator")
    port = values.get("POSTGRES_PORT", "5434")
    return f"postgresql+psycopg2://{user}:{password}@localhost:{port}/{db}"


def get_db_url() -> str:
    # Preferred explicit env var for the app/dashboard
    url = os.getenv("TENNIS_DB_URL") or os.getenv("DATABASE_URL")
    if url:
        return url

    # Try to derive from local tennis_dagster env file
    derived = _try_build_db_url_from_tennis_dagster_env()
    if derived:
        return derived

    # Last-resort default (matches tennis_dagster defaults)
    return "postgresql+psycopg2://tennis:tennis@localhost:5434/tennis_simulator"


def get_engine() -> Engine:
    return create_engine(get_db_url(), pool_pre_ping=True)





