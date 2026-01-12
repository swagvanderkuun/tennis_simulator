from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    create_engine,
    text,
)
from sqlalchemy.engine import Engine


APP_SCHEMA = "tennis"


def create_db_engine(database_url: str) -> Engine:
    # Use pool_pre_ping for long-running daemon stability
    return create_engine(database_url, pool_pre_ping=True)


def ensure_app_schema(engine: Engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {APP_SCHEMA}"))


def get_metadata() -> MetaData:
    return MetaData(schema=APP_SCHEMA)


def define_tables(metadata: MetaData) -> dict[str, Table]:
    players = Table(
        "players",
        metadata,
        Column("id", BigInteger, primary_key=True),
        Column("gender", String(10), nullable=False),  # "men" | "women"
        Column("canonical_name", Text, nullable=False),
        Column("country", String(3), nullable=True),
        Column("created_at", DateTime(timezone=True), nullable=False),
        Column("updated_at", DateTime(timezone=True), nullable=False),
        UniqueConstraint("gender", "canonical_name", name="uq_players_gender_name"),
    )

    player_aliases = Table(
        "player_aliases",
        metadata,
        Column("id", BigInteger, primary_key=True),
        Column("player_id", BigInteger, ForeignKey(f"{APP_SCHEMA}.players.id"), nullable=False),
        Column("source", String(50), nullable=False),  # "tennisabstract", "draw", etc.
        Column("alias", Text, nullable=False),
        Column("created_at", DateTime(timezone=True), nullable=False),
        UniqueConstraint("source", "alias", name="uq_alias_source_alias"),
    )

    elo_snapshots = Table(
        "elo_snapshots",
        metadata,
        Column("id", BigInteger, primary_key=True),
        Column("gender", String(10), nullable=False),
        Column("scraped_at", DateTime(timezone=True), nullable=False),
        Column("source_elo_url", Text, nullable=True),
        Column("source_yelo_url", Text, nullable=True),
        Column("status", String(20), nullable=False),  # "success" | "failed"
        Column("error", Text, nullable=True),
    )

    elo_ratings = Table(
        "elo_ratings",
        metadata,
        Column("id", BigInteger, primary_key=True),
        Column("snapshot_id", BigInteger, ForeignKey(f"{APP_SCHEMA}.elo_snapshots.id"), nullable=False),
        Column("player_id", BigInteger, ForeignKey(f"{APP_SCHEMA}.players.id"), nullable=False),
        Column("player_name", Text, nullable=True),  # denormalized from players.canonical_name
        Column("elo_rank", Integer, nullable=True),
        Column("elo", Float, nullable=True),
        Column("helo", Float, nullable=True),
        Column("celo", Float, nullable=True),
        Column("gelo", Float, nullable=True),
        Column("yelo", Float, nullable=True),
        Column("rank", Integer, nullable=True),
        UniqueConstraint("snapshot_id", "player_id", name="uq_snapshot_player"),
    )

    elo_current = Table(
        "elo_current",
        metadata,
        Column("id", BigInteger, primary_key=True),
        Column("gender", String(10), nullable=False),
        Column("player_id", BigInteger, ForeignKey(f"{APP_SCHEMA}.players.id"), nullable=False),
        Column("player_name", Text, nullable=False),
        Column("as_of", DateTime(timezone=True), nullable=False),  # snapshot scraped_at
        Column("source_snapshot_id", BigInteger, ForeignKey(f"{APP_SCHEMA}.elo_snapshots.id"), nullable=False),
        Column("elo_rank", Integer, nullable=True),
        Column("elo", Float, nullable=True),
        Column("helo", Float, nullable=True),
        Column("celo", Float, nullable=True),
        Column("gelo", Float, nullable=True),
        Column("yelo", Float, nullable=True),
        Column("rank", Integer, nullable=True),
        UniqueConstraint("gender", "player_id", name="uq_elo_current_gender_player"),
    )

    # Draws / tiers tables will be added next; reserved here to keep schema cohesive.
    draws = Table(
        "draws",
        metadata,
        Column("id", BigInteger, primary_key=True),
        Column("tournament", String(10), nullable=False),  # AO/RG/WIM/USO
        Column("year", Integer, nullable=False),
        Column("gender", String(10), nullable=False),
        Column("source_url", Text, nullable=False),
        Column("scraped_at", DateTime(timezone=True), nullable=True),
        Column("status", String(20), nullable=False),
        UniqueConstraint("tournament", "year", "gender", name="uq_draw_identity"),
    )

    tier_sets = Table(
        "tier_sets",
        metadata,
        Column("id", BigInteger, primary_key=True),
        Column("name", Text, nullable=False),
        Column("gender", String(10), nullable=True),
        Column("tournament", String(10), nullable=True),
        Column("year", Integer, nullable=True),
        Column("active", Integer, nullable=False, server_default=text("0")),
        Column("created_at", DateTime(timezone=True), nullable=False),
    )

    tier_assignments = Table(
        "tier_assignments",
        metadata,
        Column("id", BigInteger, primary_key=True),
        Column("tier_set_id", BigInteger, ForeignKey(f"{APP_SCHEMA}.tier_sets.id"), nullable=False),
        Column("player_id", BigInteger, ForeignKey(f"{APP_SCHEMA}.players.id"), nullable=False),
        Column("tier", String(1), nullable=False),  # A-D
        UniqueConstraint("tier_set_id", "player_id", name="uq_tier_set_player"),
    )

    draw_sources = Table(
        "draw_sources",
        metadata,
        Column("id", BigInteger, primary_key=True),
        Column("tour", String(10), nullable=False),  # atp | wta
        Column("tournament_name", Text, nullable=False),
        Column("season_year", Integer, nullable=False),
        Column("event", String(20), nullable=False, server_default=text("'singles'")),
        Column("source_url", Text, nullable=False),
        Column("active", Integer, nullable=False, server_default=text("1")),
        Column("created_at", DateTime(timezone=True), nullable=False),
        UniqueConstraint("source_url", name="uq_draw_source_url"),
    )

    draw_snapshots = Table(
        "draw_snapshots",
        metadata,
        Column("id", BigInteger, primary_key=True),
        Column("source_id", BigInteger, ForeignKey(f"{APP_SCHEMA}.draw_sources.id"), nullable=False),
        Column("scraped_at", DateTime(timezone=True), nullable=False),
        Column("status", String(20), nullable=False),  # success | failed
        Column("error", Text, nullable=True),
    )

    draw_entries = Table(
        "draw_entries",
        metadata,
        Column("id", BigInteger, primary_key=True),
        Column("snapshot_id", BigInteger, ForeignKey(f"{APP_SCHEMA}.draw_snapshots.id"), nullable=False),
        Column("part_index", Integer, nullable=False),  # 1-based
        Column("slot_index", Integer, nullable=False),  # 1..8 within part
        Column("seed_text", Text, nullable=True),       # e.g. "(1)", "(WC)"
        Column("player_name", Text, nullable=False),
        Column("is_bye", Integer, nullable=False, server_default=text("0")),
        Column("player_id", BigInteger, ForeignKey(f"{APP_SCHEMA}.players.id"), nullable=True),
        UniqueConstraint("snapshot_id", "part_index", "slot_index", name="uq_draw_entry_slot"),
    )

    draw_matches = Table(
        "draw_matches",
        metadata,
        Column("id", BigInteger, primary_key=True),
        Column("snapshot_id", BigInteger, ForeignKey(f"{APP_SCHEMA}.draw_snapshots.id"), nullable=False),
        Column("round", String(10), nullable=False),     # R32/R16/QF/SF/F
        Column("match_index", Integer, nullable=False),  # 1..N within round
        Column("entry1_id", BigInteger, ForeignKey(f"{APP_SCHEMA}.draw_entries.id"), nullable=True),
        Column("entry2_id", BigInteger, ForeignKey(f"{APP_SCHEMA}.draw_entries.id"), nullable=True),
        Column("child_match1_id", BigInteger, ForeignKey(f"{APP_SCHEMA}.draw_matches.id"), nullable=True),
        Column("child_match2_id", BigInteger, ForeignKey(f"{APP_SCHEMA}.draw_matches.id"), nullable=True),
        UniqueConstraint("snapshot_id", "round", "match_index", name="uq_draw_match_round_index"),
    )

    return {
        "players": players,
        "player_aliases": player_aliases,
        "elo_snapshots": elo_snapshots,
        "elo_ratings": elo_ratings,
        "elo_current": elo_current,
        "draws": draws,
        "tier_sets": tier_sets,
        "tier_assignments": tier_assignments,
        "draw_sources": draw_sources,
        "draw_snapshots": draw_snapshots,
        "draw_entries": draw_entries,
        "draw_matches": draw_matches,
    }


def create_app_tables(engine: Engine) -> dict[str, Table]:
    ensure_app_schema(engine)
    metadata = get_metadata()
    tables = define_tables(metadata)
    metadata.create_all(engine)

    # Lightweight migrations (we don't use Alembic yet).
    # Keep this list small and additive-only; use IF NOT EXISTS.
    with engine.begin() as conn:
        conn.execute(text(f"ALTER TABLE {APP_SCHEMA}.elo_ratings ADD COLUMN IF NOT EXISTS elo_rank integer"))
        conn.execute(text(f"ALTER TABLE {APP_SCHEMA}.elo_ratings ADD COLUMN IF NOT EXISTS player_name text"))
        # Backfill for existing rows (safe + idempotent)
        conn.execute(
            text(
                f"""
                UPDATE {APP_SCHEMA}.elo_ratings r
                SET player_name = p.canonical_name
                FROM {APP_SCHEMA}.players p
                WHERE r.player_id = p.id AND (r.player_name IS NULL OR r.player_name = '')
                """
            )
        )

        # Normalize denormalized name fields (NBSP -> space, collapse whitespace, trim).
        # Postgres doesn't have a great built-in "collapse whitespace", so use regexp_replace.
        conn.execute(
            text(
                f"""
                UPDATE {APP_SCHEMA}.elo_ratings
                SET player_name = btrim(regexp_replace(replace(player_name, chr(160), ' '), '\\s+', ' ', 'g'))
                WHERE player_name IS NOT NULL
                """
            )
        )
        conn.execute(
            text(
                f"""
                UPDATE {APP_SCHEMA}.elo_current
                SET player_name = btrim(regexp_replace(replace(player_name, chr(160), ' '), '\\s+', ' ', 'g'))
                WHERE player_name IS NOT NULL
                """
            )
        )

        # Normalize canonical_name where it would NOT create a uniqueness collision.
        # If a collision would occur, we skip updating that row to avoid breaking uq constraint.
        conn.execute(
            text(
                f"""
                WITH norm AS (
                  SELECT
                    id,
                    gender,
                    canonical_name,
                    btrim(regexp_replace(replace(canonical_name, chr(160), ' '), '\\s+', ' ', 'g')) AS canonical_name_norm
                  FROM {APP_SCHEMA}.players
                )
                UPDATE {APP_SCHEMA}.players p
                SET canonical_name = n.canonical_name_norm,
                    updated_at = now()
                FROM norm n
                WHERE p.id = n.id
                  AND n.canonical_name_norm <> n.canonical_name
                  AND NOT EXISTS (
                    SELECT 1
                    FROM {APP_SCHEMA}.players p2
                    WHERE p2.gender = n.gender
                      AND p2.canonical_name = n.canonical_name_norm
                      AND p2.id <> n.id
                  )
                """
            )
        )

    return tables


