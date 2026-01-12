from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .tennisabstract import normalize_player_name, _ua_headers


@dataclass(frozen=True)
class DrawEntry:
    part_index: int          # 1-based
    slot_index: int          # 1..8 within part
    player_name: str         # normalized
    is_bye: bool
    seed_text: Optional[str] # e.g. "(1)", "(WC)", "(Q)"


@dataclass(frozen=True)
class DrawParseResult:
    tour: str                 # atp|wta
    season_year: int
    tournament_name: str
    event: str                # singles (for now)
    entries: list[DrawEntry]  # in part/slot order


def fetch_page(url: str) -> str:
    resp = requests.get(url, headers=_ua_headers(), timeout=30)
    resp.raise_for_status()
    return resp.text


def _extract_js_string_var(html: str, var_name: str) -> str:
    # Variables look like: var proj32 = '<table ... </table>';
    m = re.search(rf"var\s+{re.escape(var_name)}\s*=\s*'(.*?)';\s*\n", html, re.S)
    if not m:
        raise ValueError(f"Could not find JS variable {var_name}")
    return m.group(1)


def _parse_tournament_meta(soup: BeautifulSoup) -> tuple[str, int, str]:
    # Expected somewhere in <h2>: "2026 ATP Adelaide" or "2026 WTA Adelaide"
    h2_candidates = [normalize_player_name(h.get_text(" ", strip=True)) for h in soup.find_all("h2")]
    title = ""
    for cand in h2_candidates:
        if re.match(r"^\d{4}\s+(ATP|WTA)\b", cand):
            title = cand
            break
    if not title:
        # Fallback: use first h2 text for debugging
        title = h2_candidates[0] if h2_candidates else ""
    # Robust parse: locate year and tour token without relying on strict whitespace matching
    m_year = re.search(r"(\d{4})", title)
    if not m_year:
        raise ValueError(f"Could not parse season year from <h2> candidates: {h2_candidates!r}")
    year = int(m_year.group(1))

    if "ATP" in title:
        tour = "atp"
        name = title.replace(str(year), "", 1).replace("ATP", "", 1)
    elif "WTA" in title:
        tour = "wta"
        name = title.replace(str(year), "", 1).replace("WTA", "", 1)
    else:
        raise ValueError(f"Could not parse tour (ATP/WTA) from <h2> candidates: {h2_candidates!r}")

    name = normalize_player_name(name)
    return tour, year, name


def parse_singles_forecast_draw(html: str) -> DrawParseResult:
    soup = BeautifulSoup(html, "html.parser")
    tour, year, tournament_name = _parse_tournament_meta(soup)

    # "Singles Forecast" uses embedded HTML tables stored in JS vars.
    # The *initial* draw is always the largest projN table available (proj128 for slams, proj32 for Adelaide, etc.).
    proj_vars = re.findall(r"\bvar\s+(proj(\d+))\s*=\s*'", html)
    if not proj_vars:
        raise ValueError("Could not find any projN JS variables (proj32/proj64/proj128) on page")
    # pick max N
    best_var, best_n = max(((name, int(n)) for name, n in proj_vars), key=lambda x: x[1])
    proj_html = _extract_js_string_var(html, best_var)
    table_soup = BeautifulSoup(proj_html, "html.parser")

    # Extract first column text for each <tr>. Blank rows separate parts.
    raw_rows: list[str] = []
    for tr in table_soup.find_all("tr"):
        tds = tr.find_all("td")
        if not tds:
            continue
        raw_rows.append(tds[0].get_text(" ", strip=True))

    # Split into parts on blank rows
    parts: list[list[str]] = []
    cur: list[str] = []
    for r in raw_rows:
        if not normalize_player_name(r):
            if cur:
                parts.append(cur)
                cur = []
            continue
        cur.append(r)
    if cur:
        parts.append(cur)

    entries: list[DrawEntry] = []
    part_index = 0
    for p in parts:
        # Each part starts with a header row "Player"
        rows = [normalize_player_name(x) for x in p if normalize_player_name(x).lower() != "player"]
        if len(rows) != 8:
            raise ValueError(f"Expected 8 entries per part, got {len(rows)}: {rows}")
        part_index += 1
        for i, cell in enumerate(rows, start=1):
            if normalize_player_name(cell).lower() == "bye":
                entries.append(DrawEntry(part_index, i, "BYE", True, None))
                continue

            # Parse seed/wc/q prefixes in parentheses at the start (can be multiple? keep first)
            seed_text = None
            m = re.match(r"^(\([^\)]+\))\s+(.*)$", cell)
            name_country = cell
            if m:
                seed_text = m.group(1)
                name_country = m.group(2)

            # Drop trailing country code "(ESP)"
            name_country = re.sub(r"\([A-Z]{3}\)\s*$", "", name_country).strip()
            player_name = normalize_player_name(name_country)
            entries.append(DrawEntry(part_index, i, player_name, False, seed_text))

    return DrawParseResult(
        tour=tour,
        season_year=year,
        tournament_name=tournament_name,
        event="singles",
        entries=entries,
    )


