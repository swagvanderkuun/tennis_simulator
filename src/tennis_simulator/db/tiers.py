from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import text
from sqlalchemy.engine import Engine


TIERS = ["A", "B", "C", "D"]


def ensure_tier_tables(engine: Engine) -> None:
    """
    Ensure the minimal tier tables exist. (Dagster scraper also creates these,
    but this keeps the dashboard usable standalone.)
    """
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS tennis"))
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS tennis.tier_sets (
                  id bigserial PRIMARY KEY,
                  name text NOT NULL,
                  gender varchar(10),
                  tournament varchar(10),
                  year integer,
                  active integer NOT NULL DEFAULT 0,
                  created_at timestamptz NOT NULL
                )
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS tennis.tier_assignments (
                  id bigserial PRIMARY KEY,
                  tier_set_id bigint NOT NULL REFERENCES tennis.tier_sets(id),
                  player_id bigint NOT NULL REFERENCES tennis.players(id),
                  tier varchar(1) NOT NULL,
                  UNIQUE (tier_set_id, player_id)
                )
                """
            )
        )


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def list_tier_sets(engine: Engine, gender: str) -> list[dict]:
    with engine.begin() as conn:
        rows = conn.execute(
            text(
                """
                SELECT id, name, gender, tournament, year, active, created_at
                FROM tennis.tier_sets
                WHERE gender = :gender
                ORDER BY created_at DESC, id DESC
                """
            ),
            {"gender": gender},
        ).mappings().all()
        return [dict(r) for r in rows]


def get_active_tier_set_id(engine: Engine, gender: str) -> int | None:
    with engine.begin() as conn:
        row = conn.execute(
            text(
                """
                SELECT id
                FROM tennis.tier_sets
                WHERE gender = :gender AND active = 1
                ORDER BY created_at DESC, id DESC
                LIMIT 1
                """
            ),
            {"gender": gender},
        ).scalar_one_or_none()
        return int(row) if row is not None else None


def set_active_tier_set(engine: Engine, gender: str, tier_set_id: int) -> None:
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE tennis.tier_sets SET active=0 WHERE gender=:gender"),
            {"gender": gender},
        )
        conn.execute(
            text("UPDATE tennis.tier_sets SET active=1 WHERE id=:id"),
            {"id": tier_set_id},
        )


def create_tier_set(engine: Engine, *, name: str, gender: str, tournament: str | None, year: int | None, make_active: bool) -> int:
    created_at = _now_utc()
    with engine.begin() as conn:
        new_id = conn.execute(
            text(
                """
                INSERT INTO tennis.tier_sets (name, gender, tournament, year, active, created_at)
                VALUES (:name, :gender, :tournament, :year, :active, :created_at)
                RETURNING id
                """
            ),
            {
                "name": name,
                "gender": gender,
                "tournament": tournament,
                "year": year,
                "active": 1 if make_active else 0,
                "created_at": created_at,
            },
        ).scalar_one()
        tier_set_id = int(new_id)

    if make_active:
        set_active_tier_set(engine, gender, tier_set_id)
    return tier_set_id


def copy_tier_set(engine: Engine, *, from_tier_set_id: int, name: str, gender: str, tournament: str | None, year: int | None, make_active: bool) -> int:
    new_id = create_tier_set(engine, name=name, gender=gender, tournament=tournament, year=year, make_active=make_active)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO tennis.tier_assignments (tier_set_id, player_id, tier)
                SELECT :new_id, player_id, tier
                FROM tennis.tier_assignments
                WHERE tier_set_id = :old_id
                """
            ),
            {"new_id": new_id, "old_id": from_tier_set_id},
        )
    return new_id


def load_tiers(engine: Engine, tier_set_id: int) -> list[dict]:
    with engine.begin() as conn:
        rows = conn.execute(
            text(
                """
                SELECT
                  p.canonical_name AS player_name,
                  ta.tier AS tier
                FROM tennis.tier_assignments ta
                JOIN tennis.players p ON p.id = ta.player_id
                WHERE ta.tier_set_id = :tier_set_id
                ORDER BY p.canonical_name
                """
            ),
            {"tier_set_id": tier_set_id},
        ).mappings().all()
        return [dict(r) for r in rows]


def upsert_tiers(engine: Engine, *, tier_set_id: int, gender: str, tiers: dict[str, str]) -> None:
    """
    tiers: mapping canonical_name -> tier letter
    """
    with engine.begin() as conn:
        for name, tier in tiers.items():
            if tier not in TIERS:
                raise ValueError(f"Invalid tier for {name}: {tier}")
            player_id = conn.execute(
                text(
                    """
                    SELECT id FROM tennis.players
                    WHERE gender=:gender AND canonical_name=:name
                    """
                ),
                {"gender": gender, "name": name},
            ).scalar_one_or_none()
            if player_id is None:
                # Create the player row if missing (country unknown here)
                player_id = conn.execute(
                    text(
                        """
                        INSERT INTO tennis.players (gender, canonical_name, country, created_at, updated_at)
                        VALUES (:gender, :name, NULL, now(), now())
                        RETURNING id
                        """
                    ),
                    {"gender": gender, "name": name},
                ).scalar_one()

            conn.execute(
                text(
                    """
                    INSERT INTO tennis.tier_assignments (tier_set_id, player_id, tier)
                    VALUES (:tier_set_id, :player_id, :tier)
                    ON CONFLICT (tier_set_id, player_id)
                    DO UPDATE SET tier = EXCLUDED.tier
                    """
                ),
                {"tier_set_id": tier_set_id, "player_id": int(player_id), "tier": tier},
            )


def ensure_tier_set_has_all_elo_current_players(engine: Engine, *, tier_set_id: int, gender: str, default_tier: str = "D") -> int:
    """
    Ensure every player present in tennis.elo_current for the given gender has a tier assignment
    in the given tier_set_id. Missing players are inserted with default_tier (default: D).

    Returns: number of assignments inserted.
    """
    if default_tier not in TIERS:
        raise ValueError(f"Invalid default_tier: {default_tier}")

    with engine.begin() as conn:
        res = conn.execute(
            text(
                """
                WITH missing AS (
                  SELECT ec.player_id
                  FROM tennis.elo_current ec
                  WHERE ec.gender = :gender
                  EXCEPT
                  SELECT ta.player_id
                  FROM tennis.tier_assignments ta
                  WHERE ta.tier_set_id = :tier_set_id
                )
                INSERT INTO tennis.tier_assignments (tier_set_id, player_id, tier)
                SELECT :tier_set_id, m.player_id, :tier
                FROM missing m
                ON CONFLICT (tier_set_id, player_id) DO NOTHING
                """
            ),
            {"tier_set_id": tier_set_id, "gender": gender, "tier": default_tier},
        )
        # rowcount is driver-dependent for INSERT..SELECT; but psycopg2 provides it.
        return int(res.rowcount or 0)


