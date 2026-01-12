from __future__ import annotations

import os
from dataclasses import dataclass

from dagster import ConfigurableResource


class DatabaseResource(ConfigurableResource):
    """Holds connection info for the tennis Postgres DB used by scraper assets."""

    database_url: str

    @staticmethod
    def from_env() -> "DatabaseResource":
        url = os.getenv("DATABASE_URL")
        if not url:
            raise RuntimeError("DATABASE_URL is not set")
        return DatabaseResource(database_url=url)


