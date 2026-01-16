from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine import Engine

from .db import create_app_tables
from .draws_tennisabstract import DrawParseResult


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def upsert_draw_source(engine: Engine, parsed: DrawParseResult, source_url: str) -> int:
    tables = create_app_tables(engine)
    draw_sources = tables["draw_sources"]
    created_at = _now_utc()

    with engine.begin() as conn:
        res = conn.execute(
            pg_insert(draw_sources)
            .values(
                tour=parsed.tour,
                tournament_name=parsed.tournament_name,
                season_year=parsed.season_year,
                event=parsed.event,
                source_url=source_url,
                active=1,
                created_at=created_at,
            )
            .on_conflict_do_update(
                index_elements=[draw_sources.c.source_url],
                set_={
                    "tour": parsed.tour,
                    "tournament_name": parsed.tournament_name,
                    "season_year": parsed.season_year,
                    "event": parsed.event,
                    "active": 1,
                },
            )
            .returning(draw_sources.c.id)
        ).scalar_one()
        return int(res)


def insert_draw_snapshot(engine: Engine, source_id: int, status: str, error: Optional[str]) -> int:
    tables = create_app_tables(engine)
    draw_snapshots = tables["draw_snapshots"]
    scraped_at = _now_utc()
    with engine.begin() as conn:
        sid = conn.execute(
            draw_snapshots.insert()
            .values(
                source_id=source_id,
                scraped_at=scraped_at,
                status=status,
                error=error,
            )
            .returning(draw_snapshots.c.id)
        ).scalar_one()
        return int(sid)


def store_draw_snapshot(engine: Engine, snapshot_id: int, parsed: DrawParseResult) -> None:
    tables = create_app_tables(engine)
    entries_t = tables["draw_entries"]
    matches_t = tables["draw_matches"]

    # Insert entries and keep ids by (part, slot)
    entry_id_map: dict[tuple[int, int], int] = {}
    with engine.begin() as conn:
        for e in parsed.entries:
            eid = conn.execute(
                entries_t.insert()
                .values(
                    snapshot_id=snapshot_id,
                    part_index=e.part_index,
                    slot_index=e.slot_index,
                    seed_text=e.seed_text,
                    player_name=e.player_name,
                    is_bye=1 if e.is_bye else 0,
                    player_id=None,
                )
                .returning(entries_t.c.id)
            ).scalar_one()
            entry_id_map[(e.part_index, e.slot_index)] = int(eid)

        # Build leaf match nodes in bracket order (pair adjacent slots within each part)
        # Leaf round label is based on total draw size
        parts = max(e.part_index for e in parsed.entries) if parsed.entries else 0
        draw_size = parts * 8
        if draw_size == 32:
            rounds = ["R32", "R16", "QF", "SF", "F"]
        elif draw_size == 64:
            rounds = ["R64", "R32", "R16", "QF", "SF", "F"]
        elif draw_size == 128:
            rounds = ["R128", "R64", "R32", "R16", "QF", "SF", "F"]
        else:
            # Fallback: label first round as R{draw_size}
            rounds = [f"R{draw_size}"]
            # then halve until 2
            n = draw_size // 2
            while n >= 2:
                rounds.append("F" if n == 2 else f"R{n}")
                n //= 2

        leaf_round = rounds[0]
        leaf_matches: list[int] = []
        match_id_by_round_index: dict[tuple[str, int], int] = {}

        leaf_match_index = 0
        for part in range(1, parts + 1):
            pairs = [(1, 2), (3, 4), (5, 6), (7, 8)]
            for a, b in pairs:
                leaf_match_index += 1
                mid = conn.execute(
                    matches_t.insert()
                    .values(
                        snapshot_id=snapshot_id,
                        round=leaf_round,
                        match_index=leaf_match_index,
                        entry1_id=entry_id_map[(part, a)],
                        entry2_id=entry_id_map[(part, b)],
                        child_match1_id=None,
                        child_match2_id=None,
                    )
                    .returning(matches_t.c.id)
                ).scalar_one()
                mid = int(mid)
                leaf_matches.append(mid)
                match_id_by_round_index[(leaf_round, leaf_match_index)] = mid

        # Build subsequent rounds by pairing adjacent matches
        prev_round_matches = leaf_matches
        for rnd in rounds[1:]:
            next_round_matches: list[int] = []
            idx = 0
            match_index = 0
            while idx < len(prev_round_matches):
                match_index += 1
                m1 = prev_round_matches[idx]
                m2 = prev_round_matches[idx + 1]
                idx += 2
                mid = conn.execute(
                    matches_t.insert()
                    .values(
                        snapshot_id=snapshot_id,
                        round=rnd,
                        match_index=match_index,
                        entry1_id=None,
                        entry2_id=None,
                        child_match1_id=m1,
                        child_match2_id=m2,
                    )
                    .returning(matches_t.c.id)
                ).scalar_one()
                next_round_matches.append(int(mid))
                match_id_by_round_index[(rnd, match_index)] = int(mid)
            prev_round_matches = next_round_matches




