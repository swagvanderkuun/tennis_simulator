from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Optional

from sqlalchemy import Table, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine import Engine

from .tennisexplorer_injuries import InjuryReportRow, to_name_key


@dataclass(frozen=True)
class InjuryMatchResult:
    matched_player_id: Optional[int]
    matched_gender: Optional[str]
    method: str  # exact | alias | fuzzy | none
    score: Optional[float]
    candidate_count: int
    ambiguous: bool
    notes: Optional[str]


@dataclass(frozen=True)
class InjuryMatchEvaluation:
    total: int
    matched: int
    unmatched: int
    ambiguous: int
    avg_score: float


def _similarity(a: str, b: str) -> float:
    # SequenceMatcher is cheap and dependency-free; good enough for last-resort matching.
    return SequenceMatcher(None, a, b).ratio()


def _name_key_variants(key: str) -> list[str]:
    """
    Generate variants that help with common cross-site formatting differences:
    - "lastname firstname" vs "firstname lastname" (two-token swap)
    """
    k = (key or "").strip()
    if not k:
        return []
    toks = k.split()
    if len(toks) == 2:
        swapped = f"{toks[1]} {toks[0]}"
        if swapped != k:
            return [k, swapped]
    return [k]


def match_player_for_injury_report(
    conn,
    *,
    report: InjuryReportRow,
    players: Table,
    aliases: Table,
    score_threshold: float = 0.86,
) -> InjuryMatchResult:
    """
    Match a TennisExplorer injury row to a player in tennis.players.

    Strategy (in order):
    - exact normalized match against players.canonical_name (both genders)
    - exact alias match against player_aliases.alias (source 'tennisexplorer'/'tennisabstract'/etc)
    - fuzzy match against canonical names using a normalized name_key + SequenceMatcher
    """
    # 1) Exact match on canonical_name (case/space normalized).
    q_exact = select(players.c.id, players.c.gender).where(players.c.canonical_name == report.player_name)
    exact = conn.execute(q_exact).fetchall()
    if len(exact) == 1:
        pid, gender = exact[0]
        return InjuryMatchResult(
            matched_player_id=int(pid),
            matched_gender=str(gender),
            method="exact",
            score=1.0,
            candidate_count=1,
            ambiguous=False,
            notes=None,
        )
    if len(exact) > 1:
        return InjuryMatchResult(
            matched_player_id=None,
            matched_gender=None,
            method="exact",
            score=1.0,
            candidate_count=len(exact),
            ambiguous=True,
            notes="Multiple players share same canonical_name across genders",
        )

    # 2) Exact match via aliases.
    q_alias = (
        select(players.c.id, players.c.gender)
        .select_from(aliases.join(players, aliases.c.player_id == players.c.id))
        .where(aliases.c.alias == report.player_name)
    )
    alias_hits = conn.execute(q_alias).fetchall()
    if len(alias_hits) == 1:
        pid, gender = alias_hits[0]
        return InjuryMatchResult(
            matched_player_id=int(pid),
            matched_gender=str(gender),
            method="alias",
            score=1.0,
            candidate_count=1,
            ambiguous=False,
            notes=None,
        )
    if len(alias_hits) > 1:
        return InjuryMatchResult(
            matched_player_id=None,
            matched_gender=None,
            method="alias",
            score=1.0,
            candidate_count=len(alias_hits),
            ambiguous=True,
            notes="Multiple alias matches found",
        )

    # 3) Fuzzy match (best effort).
    key = report.player_name_norm or to_name_key(report.player_name)
    if not key:
        return InjuryMatchResult(
            matched_player_id=None,
            matched_gender=None,
            method="none",
            score=None,
            candidate_count=0,
            ambiguous=False,
            notes="Empty name key",
        )

    # Use a small candidate pool by filtering on last token.
    tokens = key.split()
    last = tokens[-1] if tokens else ""
    cand_q = select(players.c.id, players.c.gender, players.c.canonical_name)
    if last:
        cand_q = cand_q.where(players.c.canonical_name.ilike(f"%{last}%"))
    candidates = conn.execute(cand_q).fetchall()
    if not candidates:
        return InjuryMatchResult(
            matched_player_id=None,
            matched_gender=None,
            method="none",
            score=None,
            candidate_count=0,
            ambiguous=False,
            notes=f"No candidates for last_token={last!r}",
        )

    scored: list[tuple[float, int, str]] = []
    key_variants = _name_key_variants(key)
    for pid, gender, cname in candidates:
        ckey = to_name_key(cname or "")
        c_variants = _name_key_variants(ckey)
        # Compare across variants to account for "Last First" vs "First Last"
        s = 0.0
        for a in key_variants:
            for b in c_variants:
                s = max(s, _similarity(a, b))
        scored.append((s, int(pid), str(gender)))
    scored.sort(reverse=True, key=lambda x: x[0])
    best_score, best_pid, best_gender = scored[0]
    second_score = scored[1][0] if len(scored) > 1 else 0.0

    if best_score >= score_threshold:
        ambiguous = abs(best_score - second_score) < 0.02 and second_score >= score_threshold
        return InjuryMatchResult(
            matched_player_id=None if ambiguous else best_pid,
            matched_gender=None if ambiguous else best_gender,
            method="fuzzy",
            score=float(best_score),
            candidate_count=len(candidates),
            ambiguous=bool(ambiguous),
            notes="Top-2 scores too close" if ambiguous else None,
        )

    return InjuryMatchResult(
        matched_player_id=None,
        matched_gender=None,
        method="none",
        score=float(best_score),
        candidate_count=len(candidates),
        ambiguous=False,
        notes=f"Below threshold {score_threshold:.2f}",
    )


def upsert_injury_reports(
    conn,
    *,
    injury_reports: Table,
    scraped_at: datetime,
    rows: list[InjuryReportRow],
) -> int:
    inserted = 0
    for r in rows:
        res = conn.execute(
            pg_insert(injury_reports)
            .values(
                scraped_at=scraped_at,
                status=r.status,
                start_date=r.start_date,
                player_name=r.player_name,
                player_name_norm=r.player_name_norm,
                player_profile_url=r.player_profile_url,
                tournament=r.tournament,
                reason=r.reason,
                source_url=r.source_url,
            )
            .on_conflict_do_update(
                constraint="uq_injury_reports_identity",
                set_={
                    # Refresh these fields daily (safe + idempotent)
                    "scraped_at": scraped_at,
                    "player_name": r.player_name,
                    "player_name_norm": r.player_name_norm,
                    "player_profile_url": r.player_profile_url,
                    "tournament": r.tournament,
                    "reason": r.reason,
                    "source_url": r.source_url,
                },
            )
        )
        inserted += res.rowcount or 0
    return inserted


def match_and_store_injuries(
    engine: Engine,
    *,
    tables: dict[str, Table],
    rows: list[InjuryReportRow],
    fuzzy_threshold: float = 0.86,
) -> InjuryMatchEvaluation:
    """
    Persist scraped injury rows and (re)compute one match per injury_report_id.
    Returns aggregate match-quality stats for logging/monitoring.
    """
    injury_reports = tables["injury_reports"]
    injury_matches = tables["injury_matches"]
    players = tables["players"]
    aliases = tables["player_aliases"]

    scraped_at = datetime.now(timezone.utc)

    with engine.begin() as conn:
        upsert_injury_reports(conn, injury_reports=injury_reports, scraped_at=scraped_at, rows=rows)

        # Fetch report ids we need to match (only for today's scraped rows to keep work bounded).
        report_ids = conn.execute(
            select(injury_reports.c.id, injury_reports.c.status, injury_reports.c.start_date, injury_reports.c.player_name,
                   injury_reports.c.player_name_norm, injury_reports.c.player_profile_url, injury_reports.c.tournament,
                   injury_reports.c.reason, injury_reports.c.source_url)
            .where(injury_reports.c.scraped_at == scraped_at)
        ).fetchall()

        matched = 0
        ambiguous = 0
        score_sum = 0.0
        score_count = 0

        for row in report_ids:
            report_id = int(row[0])
            report = InjuryReportRow(
                status=str(row[1]),
                start_date=row[2],
                player_name=str(row[3]),
                player_name_norm=str(row[4] or ""),
                player_profile_url=row[5],
                tournament=row[6],
                reason=row[7],
                source_url=str(row[8]),
            )
            res = match_player_for_injury_report(
                conn,
                report=report,
                players=players,
                aliases=aliases,
                score_threshold=fuzzy_threshold,
            )

            if res.score is not None:
                score_sum += float(res.score)
                score_count += 1

            if res.ambiguous:
                ambiguous += 1
            if res.matched_player_id is not None:
                matched += 1
                # If we matched successfully, store a tennisexplorer alias for future exact matching.
                conn.execute(
                    pg_insert(aliases)
                    .values(
                        player_id=res.matched_player_id,
                        source="tennisexplorer",
                        alias=report.player_name,
                        created_at=scraped_at,
                    )
                    .on_conflict_do_nothing(index_elements=[aliases.c.source, aliases.c.alias])
                )

            conn.execute(
                pg_insert(injury_matches)
                .values(
                    injury_report_id=report_id,
                    matched_at=scraped_at,
                    matched_player_id=res.matched_player_id,
                    matched_gender=res.matched_gender,
                    match_method=res.method,
                    match_score=res.score,
                    candidate_count=res.candidate_count,
                    ambiguous=1 if res.ambiguous else 0,
                    notes=res.notes,
                )
                .on_conflict_do_update(
                    constraint="uq_injury_matches_report",
                    set_={
                        "matched_at": scraped_at,
                        "matched_player_id": res.matched_player_id,
                        "matched_gender": res.matched_gender,
                        "match_method": res.method,
                        "match_score": res.score,
                        "candidate_count": res.candidate_count,
                        "ambiguous": 1 if res.ambiguous else 0,
                        "notes": res.notes,
                    },
                )
            )

        total = len(report_ids)
        unmatched = total - matched - ambiguous if total >= (matched + ambiguous) else max(0, total - matched)
        avg_score = (score_sum / score_count) if score_count else 0.0
        return InjuryMatchEvaluation(
            total=total,
            matched=matched,
            unmatched=unmatched,
            ambiguous=ambiguous,
            avg_score=float(avg_score),
        )


