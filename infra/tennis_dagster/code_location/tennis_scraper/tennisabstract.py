from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional

import pandas as pd
import requests
from io import StringIO
import unicodedata
import time


@dataclass(frozen=True)
class EloRow:
    name: str
    elo_rank: Optional[int]
    elo: Optional[float]
    helo: Optional[float]
    celo: Optional[float]
    gelo: Optional[float]
    rank: Optional[int]


@dataclass(frozen=True)
class YEloRow:
    name: str
    yelo: Optional[float]
    yelo_rank: Optional[int]


def normalize_player_name(name: str) -> str:
    """
    Normalize player names from TennisAbstract:
    - Unicode normalize (NFKC)
    - Replace NBSP with normal spaces
    - Collapse whitespace and strip
    """
    if name is None:
        return ""
    s = unicodedata.normalize("NFKC", str(name))
    s = s.replace("\u00A0", " ")
    s = " ".join(s.split())
    return s.strip()


def _ua_headers() -> dict[str, str]:
    ua = os.getenv("SCRAPER_USER_AGENT") or "tennis_simulator_scraper/0.1"
    return {"User-Agent": ua}


def fetch_html(url: str) -> str:
    """
    Fetch HTML with light retry/backoff for 429/5xx (archive sites commonly rate-limit).
    """
    headers = _ua_headers()
    # A couple of extra headers help with some simple bot filters.
    headers.setdefault("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    headers.setdefault("Accept-Language", "en-US,en;q=0.9")

    max_attempts = int(os.getenv("SCRAPER_HTTP_MAX_ATTEMPTS") or "5")
    base_sleep = float(os.getenv("SCRAPER_HTTP_BASE_SLEEP_SECONDS") or "5")

    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                sleep_s = float(retry_after) if retry_after and retry_after.isdigit() else base_sleep * attempt
                time.sleep(min(sleep_s, 60.0))
                continue
            if 500 <= resp.status_code < 600:
                time.sleep(min(base_sleep * attempt, 30.0))
                continue
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            last_exc = e
            time.sleep(min(base_sleep * attempt, 30.0))
            continue
    raise last_exc if last_exc else RuntimeError(f"Failed to fetch {url}")


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def parse_elo_table(html: str) -> list[EloRow]:
    """
    Parse a TennisAbstract Elo table similar to the one saved as elo_men.txt in this repo.
    We expect columns that include at least: Player, Elo, and optionally hElo/cElo/gElo and ATP Rank/WTA Rank.
    """
    tables = pd.read_html(StringIO(html))
    if not tables:
        raise ValueError("No tables found in HTML")

    # TennisAbstract pages often contain a small "layout" table first, then the real data table(s).
    # Select the best candidate table by looking for required columns.
    def norm(s: str) -> str:
        return str(s).replace("\xa0", " ").strip().lower()

    best_df: Optional[pd.DataFrame] = None
    best_score = -1
    for t in tables:
        df_try = _normalize_columns(t)
        cols_norm = {norm(c): c for c in df_try.columns}
        has_player = any(k == "player" or "player" in k for k in cols_norm.keys())
        has_elo = "elo" in cols_norm
        if has_player and has_elo:
            # Prefer the largest table (more rows) to avoid picking headers/partials
            score = len(df_try)
            if score > best_score:
                best_df = df_try
                best_score = score

    if best_df is None:
        # Provide some debugging context
        col_lists = [list(_normalize_columns(t).columns) for t in tables[:5]]
        raise ValueError(f"Could not find Elo table with Player/Elo columns. First tables columns={col_lists}")

    df = best_df

    # Common column names observed
    player_col = next((c for c in df.columns if norm(c) == "player"), None)
    if not player_col:
        # fallback: first column containing 'player'
        player_col = next((c for c in df.columns if "player" in norm(c)), None)
    if not player_col:
        raise ValueError(f"Could not find Player column in columns={list(df.columns)}")

    def pick_col(*candidates: str) -> Optional[str]:
        lower_map = {norm(c): c for c in df.columns}
        for cand in candidates:
            if norm(cand) in lower_map:
                return lower_map[norm(cand)]
        return None

    elo_col = pick_col("Elo")
    elo_rank_col = pick_col("Elo Rank")
    helo_col = pick_col("hElo")
    celo_col = pick_col("cElo")
    gelo_col = pick_col("gElo")
    # Rank columns vary; accept any column containing "rank" if the explicit ones are missing.
    rank_col = pick_col("ATP Rank", "WTA Rank", "Rank")
    if not rank_col:
        rank_col = next((c for c in df.columns if "rank" in norm(c)), None)

    def to_float(v: Any) -> Optional[float]:
        try:
            if pd.isna(v):
                return None
            return float(str(v).strip())
        except Exception:
            return None

    def to_int(v: Any) -> Optional[int]:
        try:
            if pd.isna(v):
                return None
            return int(float(str(v).strip()))
        except Exception:
            return None

    out: list[EloRow] = []
    for _, row in df.iterrows():
        name = normalize_player_name(row[player_col])
        if not name or name.lower() in ("player", "nan", "none"):
            continue
        out.append(
            EloRow(
                name=name,
                elo_rank=to_int(row[elo_rank_col]) if elo_rank_col else None,
                elo=to_float(row[elo_col]) if elo_col else None,
                helo=to_float(row[helo_col]) if helo_col else None,
                celo=to_float(row[celo_col]) if celo_col else None,
                gelo=to_float(row[gelo_col]) if gelo_col else None,
                rank=to_int(row[rank_col]) if rank_col else None,
            )
        )

    if not out:
        raise ValueError("Parsed 0 Elo rows; table format likely changed")
    return out


def parse_yelo_table(html: str) -> list[YEloRow]:
    """
    Parse a TennisAbstract yElo table similar to yelo_men.txt in this repo.
    We expect columns like: Player, yElo (case-insensitive).
    """
    tables = pd.read_html(StringIO(html))
    if not tables:
        raise ValueError("No tables found in HTML")

    def norm(s: str) -> str:
        return str(s).replace("\xa0", " ").strip().lower()

    best_df: Optional[pd.DataFrame] = None
    best_score = -1
    for t in tables:
        df_try = _normalize_columns(t)
        cols_norm = {norm(c): c for c in df_try.columns}
        has_player = any(k == "player" or "player" in k for k in cols_norm.keys())
        has_yelo = any(k == "yelo" or "yelo" in k for k in cols_norm.keys())
        if has_player and has_yelo:
            score = len(df_try)
            if score > best_score:
                best_df = df_try
                best_score = score

    if best_df is None:
        col_lists = [list(_normalize_columns(t).columns) for t in tables[:5]]
        raise ValueError(f"Could not find yElo table with Player/yElo columns. First tables columns={col_lists}")

    df = best_df

    player_col = next((c for c in df.columns if norm(c) == "player"), None)
    if not player_col:
        player_col = next((c for c in df.columns if "player" in norm(c)), None)
    if not player_col:
        raise ValueError(f"Could not find Player column in columns={list(df.columns)}")

    # yElo pages include a rank column which is effectively the yElo rank on that report.
    rank_col = next((c for c in df.columns if norm(c) == "rank"), None)
    if not rank_col:
        rank_col = next((c for c in df.columns if "rank" in norm(c)), None)

    yelo_col = next((c for c in df.columns if norm(c) == "yelo"), None)
    if not yelo_col:
        yelo_col = next((c for c in df.columns if "yelo" in norm(c)), None)
    if not yelo_col:
        raise ValueError(f"Could not find yElo column in columns={list(df.columns)}")

    def to_float(v: Any) -> Optional[float]:
        try:
            if pd.isna(v):
                return None
            return float(str(v).strip())
        except Exception:
            return None

    def to_int(v: Any) -> Optional[int]:
        try:
            if pd.isna(v):
                return None
            return int(float(str(v).strip()))
        except Exception:
            return None

    out: list[YEloRow] = []
    for _, row in df.iterrows():
        name = normalize_player_name(row[player_col])
        if not name or name.lower() in ("player", "nan", "none"):
            continue
        out.append(
            YEloRow(
                name=name,
                yelo=to_float(row[yelo_col]),
                yelo_rank=to_int(row[rank_col]) if rank_col else None,
            )
        )

    if not out:
        raise ValueError("Parsed 0 yElo rows; table format likely changed")
    return out


