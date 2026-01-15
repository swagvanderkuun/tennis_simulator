from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Optional

from dagster import Field, op, get_dagster_logger

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
            yelo_map = {
                normalize_player_name(r.name): (r.yelo, r.yelo_rank)
                for r in yelo_rows
            }

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
                    yelo_pair = yelo_map.get(name)
                    yelo_raw = yelo_pair[0] if yelo_pair else None
                    yelo_rank = yelo_pair[1] if yelo_pair else None
                    # TA season yElo report only includes players with >=5 wins in current year.
                    # For downstream usability, fill missing yElo with overall Elo, but keep raw value + flag.
                    yelo_imputed = 1 if yelo_raw is None else 0
                    yelo_val = yelo_raw if yelo_raw is not None else r.elo
                    conn.execute(
                        ratings.insert().values(
                            snapshot_id=snapshot_id,
                            player_id=pid,
                            player_name=name,
                            elo_rank=r.elo_rank,
                            yelo_rank=yelo_rank,
                            elo=r.elo,
                            helo=r.helo,
                            celo=r.celo,
                            gelo=r.gelo,
                            yelo=yelo_val,
                            yelo_raw=yelo_raw,
                            yelo_imputed=yelo_imputed,
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
                            yelo_rank=yelo_rank,
                            elo=r.elo,
                            helo=r.helo,
                            celo=r.celo,
                            gelo=r.gelo,
                            yelo=yelo_val,
                            yelo_raw=yelo_raw,
                            yelo_imputed=yelo_imputed,
                            rank=r.rank,
                        )
                        .on_conflict_do_update(
                            index_elements=[current.c.gender, current.c.player_id],
                            set_={
                                "player_name": name,
                                "as_of": scraped_at,
                                "source_snapshot_id": snapshot_id,
                                "elo_rank": r.elo_rank,
                                "yelo_rank": yelo_rank,
                                "elo": r.elo,
                                "helo": r.helo,
                                "celo": r.celo,
                                "gelo": r.gelo,
                                "yelo": yelo_val,
                                "yelo_raw": yelo_raw,
                                "yelo_imputed": yelo_imputed,
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
    name="backfill_elo_snapshot_op",
    config_schema={
        # The page to scrape (can be TennisAbstract or an archive snapshot like archive.is/archive.today).
        "source_url": Field(str, is_required=False),
        # Alternative: provide a path to an HTML file that exists inside the container.
        # This avoids archive site bot-blocking/429 issues. You can docker-cp the file into the container.
        "source_html_path": Field(str, is_required=False),
        # Alternative: provide a path to a zip file (e.g. archive.today "download.zip") inside the container.
        # The op will extract the first *.html file from the zip and parse it.
        "source_zip_path": Field(str, is_required=False),
        # "men" | "women"
        "gender": str,
        # "elo" | "yelo"
        "rating_type": str,
        # YYYY-MM-DD (this is the historical 'as of' date you want to store)
        "as_of_date": str,
        # Safety: default false so backfill never overwrites elo_current
        "update_current": Field(bool, is_required=False, default_value=False),
    },
)
def backfill_elo_snapshot_op(context) -> None:
    """
    Backfill historical Elo/yElo snapshots from a manually provided URL.

    This is intended for archive snapshots (e.g. archive.today) and is append-only:
    - inserts a row into tennis.elo_snapshots
    - inserts per-player rows into tennis.elo_ratings
    - by default does NOT touch tennis.elo_current (set update_current=true to opt in)
    """
    log = get_dagster_logger()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    cfg = context.op_config or {}
    source_url = (cfg.get("source_url") or "").strip()
    source_html_path = (cfg.get("source_html_path") or "").strip()
    source_zip_path = (cfg.get("source_zip_path") or "").strip()
    gender = (cfg.get("gender") or "").strip().lower()
    rating_type = (cfg.get("rating_type") or "").strip().lower()
    as_of_date = (cfg.get("as_of_date") or "").strip()
    update_current = bool(cfg.get("update_current", False))

    if gender not in ("men", "women"):
        raise ValueError("gender must be 'men' or 'women'")
    if rating_type not in ("elo", "yelo"):
        raise ValueError("rating_type must be 'elo' or 'yelo'")
    if not source_url and not source_html_path and not source_zip_path:
        raise ValueError("Provide one of: source_url, source_html_path, source_zip_path")

    try:
        as_of_dt = datetime.fromisoformat(as_of_date).replace(tzinfo=timezone.utc)
    except Exception as e:
        raise ValueError("as_of_date must be YYYY-MM-DD") from e

    engine = create_db_engine(database_url)
    tables = create_app_tables(engine)
    players = tables["players"]
    aliases = tables["player_aliases"]
    snapshots = tables["elo_snapshots"]
    ratings = tables["elo_ratings"]
    current = tables["elo_current"]

    def _bad_name(name: str) -> bool:
        n = (name or "").strip().lower()
        return n in ("", "nan", "none")

    def get_or_create_player_id(conn, canonical_name: str) -> int:
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
                created_at=as_of_dt,
                updated_at=as_of_dt,
            ).returning(players.c.id)
        ).scalar_one()

        conn.execute(
            pg_insert(aliases)
            .values(
                player_id=inserted,
                source="tennisabstract",
                alias=canonical_name,
                created_at=as_of_dt,
            )
            .on_conflict_do_nothing(index_elements=[aliases.c.source, aliases.c.alias])
        )
        return int(inserted)

    origin = source_zip_path or source_html_path or source_url
    log.info("Backfill %s %s from %s (as_of=%s) update_current=%s", gender, rating_type, origin, as_of_date, update_current)

    if source_zip_path:
        import zipfile

        with zipfile.ZipFile(source_zip_path, "r") as zf:
            # Prefer any .html files
            names = [n for n in zf.namelist() if n.lower().endswith(".html")]
            if not names:
                # Fallback: take first file
                names = zf.namelist()
            if not names:
                raise RuntimeError("Zip file is empty")
            with zf.open(names[0], "r") as f:
                html = f.read().decode("utf-8", errors="ignore")
    elif source_html_path:
        with open(source_html_path, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()
    else:
        html = fetch_html(source_url)

    with engine.begin() as conn:
        snapshot_id = int(
            conn.execute(
                snapshots.insert()
                .values(
                    gender=gender,
                    scraped_at=as_of_dt,
                    source_elo_url=source_url if rating_type == "elo" else None,
                    source_yelo_url=source_url if rating_type == "yelo" else None,
                    status="success",
                    error=None,
                )
                .returning(snapshots.c.id)
            ).scalar_one()
        )

        inserted_count = 0

        if rating_type == "elo":
            elo_rows = parse_elo_table(html)
            for r in elo_rows:
                if _bad_name(r.name):
                    continue
                name = normalize_player_name(r.name)
                pid = get_or_create_player_id(conn, name)
                conn.execute(
                    ratings.insert().values(
                        snapshot_id=snapshot_id,
                        player_id=pid,
                        player_name=name,
                        elo_rank=r.elo_rank,
                        yelo_rank=None,
                        elo=r.elo,
                        helo=r.helo,
                        celo=r.celo,
                        gelo=r.gelo,
                        yelo=None,
                        yelo_raw=None,
                        yelo_imputed=0,
                        rank=r.rank,
                    )
                )
                inserted_count += 1

                if update_current:
                    conn.execute(
                        pg_insert(current)
                        .values(
                            gender=gender,
                            player_id=pid,
                            player_name=name,
                            as_of=as_of_dt,
                            source_snapshot_id=snapshot_id,
                            elo_rank=r.elo_rank,
                            yelo_rank=None,
                            elo=r.elo,
                            helo=r.helo,
                            celo=r.celo,
                            gelo=r.gelo,
                            yelo=None,
                            yelo_raw=None,
                            yelo_imputed=0,
                            rank=r.rank,
                        )
                        .on_conflict_do_update(
                            index_elements=[current.c.gender, current.c.player_id],
                            set_={
                                "player_name": name,
                                "as_of": as_of_dt,
                                "source_snapshot_id": snapshot_id,
                                "elo_rank": r.elo_rank,
                                "yelo_rank": None,
                                "elo": r.elo,
                                "helo": r.helo,
                                "celo": r.celo,
                                "gelo": r.gelo,
                                "yelo": None,
                                "yelo_raw": None,
                                "yelo_imputed": 0,
                                "rank": r.rank,
                            },
                        )
                    )

        else:
            yelo_rows = parse_yelo_table(html)
            for r in yelo_rows:
                if _bad_name(r.name):
                    continue
                name = normalize_player_name(r.name)
                pid = get_or_create_player_id(conn, name)
                conn.execute(
                    ratings.insert().values(
                        snapshot_id=snapshot_id,
                        player_id=pid,
                        player_name=name,
                        elo_rank=None,
                        yelo_rank=r.yelo_rank,
                        elo=None,
                        helo=None,
                        celo=None,
                        gelo=None,
                        yelo=r.yelo,
                        yelo_raw=r.yelo,
                        yelo_imputed=0,
                        rank=None,
                    )
                )
                inserted_count += 1

                if update_current:
                    conn.execute(
                        pg_insert(current)
                        .values(
                            gender=gender,
                            player_id=pid,
                            player_name=name,
                            as_of=as_of_dt,
                            source_snapshot_id=snapshot_id,
                            elo_rank=None,
                            yelo_rank=r.yelo_rank,
                            elo=None,
                            helo=None,
                            celo=None,
                            gelo=None,
                            yelo=r.yelo,
                            yelo_raw=r.yelo,
                            yelo_imputed=0,
                            rank=None,
                        )
                        .on_conflict_do_update(
                            index_elements=[current.c.gender, current.c.player_id],
                            set_={
                                "player_name": name,
                                "as_of": as_of_dt,
                                "source_snapshot_id": snapshot_id,
                                "elo_rank": None,
                                "yelo_rank": r.yelo_rank,
                                "elo": None,
                                "helo": None,
                                "celo": None,
                                "gelo": None,
                                "yelo": r.yelo,
                                "yelo_raw": r.yelo,
                                "yelo_imputed": 0,
                                "rank": None,
                            },
                        )
                    )

        log.info("Backfill stored snapshot_id=%s rows=%s", snapshot_id, inserted_count)


@op(
    config_schema={
        # Default is intentionally empty so Dagster Launchpad shows the config shape,
        # but users can paste a URL to run. If empty at runtime, we fall back to
        # TA_DRAW_EXAMPLE_URL (optional) or raise.
        "source_url": Field(str, is_required=False, default_value=""),
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


