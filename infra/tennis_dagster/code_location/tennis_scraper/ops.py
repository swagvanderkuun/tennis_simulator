from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional

from dagster import op, get_dagster_logger

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from .db import create_app_tables, create_db_engine
from .draw_persist import insert_draw_snapshot, store_draw_snapshot, upsert_draw_source
from .draws_tennisabstract import fetch_page, parse_singles_forecast_draw
from .tennisabstract import fetch_html, parse_elo_table, parse_yelo_table, normalize_player_name


@op
def scrape_elo_op() -> None:
    """
    Scrape TennisAbstract Elo + yElo tables (men + women) and store snapshots in Postgres.
    URLs are configured via env:
      - TA_ELO_MEN_URL / TA_ELO_WOMEN_URL
      - TA_YELO_MEN_URL / TA_YELO_WOMEN_URL
    """
    log = get_dagster_logger()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    urls = {
        "men": {
            "elo": os.getenv("TA_ELO_MEN_URL") or "",
            "yelo": os.getenv("TA_YELO_MEN_URL") or "",
        },
        "women": {
            "elo": os.getenv("TA_ELO_WOMEN_URL") or "",
            "yelo": os.getenv("TA_YELO_WOMEN_URL") or "",
        },
    }

    missing = [
        f"{gender}:{k}"
        for gender, d in urls.items()
        for k, v in d.items()
        if not v
    ]
    if missing:
        raise RuntimeError(
            "Missing required TennisAbstract URL env vars: " + ", ".join(missing)
        )

    engine = create_db_engine(database_url)
    tables = create_app_tables(engine)
    players = tables["players"]
    aliases = tables["player_aliases"]
    snapshots = tables["elo_snapshots"]
    ratings = tables["elo_ratings"]
    current = tables["elo_current"]

    scraped_at = datetime.now(timezone.utc)
    log.info("scrape_elo_op starting at %s", scraped_at.isoformat())

    def _bad_name(name: str) -> bool:
        n = (name or "").strip().lower()
        return n in ("", "nan", "none")

    def get_or_create_player_id(conn, gender: str, canonical_name: str) -> int:
        if _bad_name(canonical_name):
            raise ValueError(f"Invalid player name: {canonical_name!r}")

        q = select(players.c.id).where(
            players.c.gender == gender,
            players.c.canonical_name == canonical_name,
        )
        existing = conn.execute(q).scalar_one_or_none()
        if existing is not None:
            return int(existing)

        inserted = conn.execute(
            players.insert().values(
                gender=gender,
                canonical_name=canonical_name,
                country=None,
                created_at=scraped_at,
                updated_at=scraped_at,
            ).returning(players.c.id)
        ).scalar_one()

        # Create a default alias for the canonical name (idempotent)
        conn.execute(
            pg_insert(aliases)
            .values(
                player_id=inserted,
                source="tennisabstract",
                alias=canonical_name,
                created_at=scraped_at,
            )
            .on_conflict_do_nothing(index_elements=[aliases.c.source, aliases.c.alias])
        )
        return int(inserted)

    errors: list[str] = []
    for gender in ("men", "women"):
        source_elo_url = urls[gender]["elo"]
        source_yelo_url = urls[gender]["yelo"]

        try:
            elo_html = fetch_html(source_elo_url)
            yelo_html = fetch_html(source_yelo_url)

            elo_rows = parse_elo_table(elo_html)
            yelo_rows = parse_yelo_table(yelo_html)
            # Names are already normalized in parse_*; normalize again defensively for map keys.
            yelo_map = {normalize_player_name(r.name): r.yelo for r in yelo_rows}

            with engine.begin() as conn:
                snapshot_id = int(
                    conn.execute(
                        snapshots.insert()
                        .values(
                            gender=gender,
                            scraped_at=scraped_at,
                            source_elo_url=source_elo_url,
                            source_yelo_url=source_yelo_url,
                            status="success",
                            error=None,
                        )
                        .returning(snapshots.c.id)
                    ).scalar_one()
                )

                inserted_count = 0
                for r in elo_rows:
                    if _bad_name(r.name):
                        continue
                    name = normalize_player_name(r.name)
                    pid = get_or_create_player_id(conn, gender, name)
                    yelo_val = yelo_map.get(name)
                    conn.execute(
                        ratings.insert().values(
                            snapshot_id=snapshot_id,
                            player_id=pid,
                            player_name=name,
                            elo_rank=r.elo_rank,
                            elo=r.elo,
                            helo=r.helo,
                            celo=r.celo,
                            gelo=r.gelo,
                            yelo=yelo_val,
                            rank=r.rank,
                        )
                    )
                    # Maintain "current" ratings by upserting on (gender, player_id).
                    conn.execute(
                        pg_insert(current)
                        .values(
                            gender=gender,
                            player_id=pid,
                            player_name=name,
                            as_of=scraped_at,
                            source_snapshot_id=snapshot_id,
                            elo_rank=r.elo_rank,
                            elo=r.elo,
                            helo=r.helo,
                            celo=r.celo,
                            gelo=r.gelo,
                            yelo=yelo_val,
                            rank=r.rank,
                        )
                        .on_conflict_do_update(
                            index_elements=[current.c.gender, current.c.player_id],
                            set_={
                                "player_name": name,
                                "as_of": scraped_at,
                                "source_snapshot_id": snapshot_id,
                                "elo_rank": r.elo_rank,
                                "elo": r.elo,
                                "helo": r.helo,
                                "celo": r.celo,
                                "gelo": r.gelo,
                                "yelo": yelo_val,
                                "rank": r.rank,
                            },
                        )
                    )
                    inserted_count += 1

                log.info(
                    "Stored Elo snapshot for gender=%s snapshot_id=%s rows=%s",
                    gender,
                    snapshot_id,
                    inserted_count,
                )

        except Exception as e:
            # Record a failed snapshot in an independent transaction.
            with engine.begin() as conn:
                conn.execute(
                    snapshots.insert().values(
                        gender=gender,
                        scraped_at=scraped_at,
                        source_elo_url=source_elo_url,
                        source_yelo_url=source_yelo_url,
                        status="failed",
                        error=str(e),
                    )
                )
            errors.append(f"{gender}: {e}")

    if errors:
        raise RuntimeError("Elo scrape completed with failures: " + " | ".join(errors))

    log.info("scrape_elo_op done")


@op(
    config_schema={
        "source_url": str,
    }
)
def scrape_draw_op(context) -> None:
    """
    Scrape a tournament draw from a TennisAbstract /current/ page.

    This op takes a URL as run config:
      ops:
        scrape_draw_op:
          config:
            source_url: "https://www.tennisabstract.com/current/2026ATPAuckland.html"
    """
    log = get_dagster_logger()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    draw_url = (context.op_config or {}).get("source_url", "").strip()
    if not draw_url:
        # Backwards-compatible fallback (optional)
        draw_url = (os.getenv("TA_DRAW_EXAMPLE_URL") or "").strip()
    if not draw_url:
        raise RuntimeError("Missing draw URL. Provide ops.scrape_draw_op.config.source_url (or set TA_DRAW_EXAMPLE_URL).")

    engine = create_db_engine(database_url)
    create_app_tables(engine)

    log.info("scrape_draw_op fetching %s", draw_url)
    html = fetch_page(draw_url)

    parsed = parse_singles_forecast_draw(html)
    log.info(
        "Parsed draw: %s %s %s entries=%s",
        parsed.season_year,
        parsed.tour.upper(),
        parsed.tournament_name,
        len(parsed.entries),
    )

    try:
        source_id = upsert_draw_source(engine, parsed, draw_url)
        snapshot_id = insert_draw_snapshot(engine, source_id, status="success", error=None)
        store_draw_snapshot(engine, snapshot_id, parsed)
        log.info("Stored draw snapshot_id=%s source_id=%s", snapshot_id, source_id)
    except Exception as e:
        # Best effort record failure snapshot
        source_id = upsert_draw_source(engine, parsed, draw_url)
        insert_draw_snapshot(engine, source_id, status="failed", error=str(e))
        raise


