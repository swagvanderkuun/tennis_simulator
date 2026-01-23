from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re
import unicodedata
from typing import Optional

from bs4 import BeautifulSoup

from .tennisabstract import fetch_html, normalize_player_name


TENNISEXPLORER_BASE = "https://www.tennisexplorer.com"
INJURED_URL = f"{TENNISEXPLORER_BASE}/list-players/injured/"
RETURNING_URL = f"{TENNISEXPLORER_BASE}/list-players/return-from-injury/"


@dataclass(frozen=True)
class InjuryReportRow:
    status: str  # injured | returning
    start_date: Optional[date]
    player_name: str
    player_name_norm: str
    player_profile_url: Optional[str]
    tournament: Optional[str]
    reason: Optional[str]
    source_url: str


def _parse_ddmmyyyy(s: str) -> Optional[date]:
    s = (s or "").strip()
    if not s:
        return None
    try:
        # TennisExplorer shows "21.01.2026"
        dd, mm, yyyy = s.split(".")
        return date(int(yyyy), int(mm), int(dd))
    except Exception:
        return None


def to_name_key(name: str) -> str:
    """
    Aggressive normalized key for cross-site matching:
    - NFKD unicode normalize
    - strip diacritics
    - keep letters/spaces only
    - collapse whitespace
    - lowercase
    """
    s = normalize_player_name(name)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r"[^a-z\s]+", " ", s)
    s = " ".join(s.split())
    return s.strip()


def _extract_player_display_name_from_profile_html(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "lxml")

    # TennisExplorer profiles usually contain an <h1> with the player name.
    h1 = soup.find("h1")
    if h1:
        txt = normalize_player_name(h1.get_text(" ", strip=True))
        # Common: "Salazar Daniel - profile"
        txt = re.sub(r"\s*-\s*profile.*$", "", txt, flags=re.IGNORECASE).strip()
        if txt:
            return txt

    # Fallback: try the <title> which often contains the player name.
    title = soup.find("title")
    if title:
        txt = normalize_player_name(title.get_text(" ", strip=True))
        # Common format: "Hugo Gaston - Player profile | TennisExplorer"
        if " - " in txt:
            left = txt.split(" - ", 1)[0].strip()
            if left:
                return left
        if txt:
            return txt

    return None


def scrape_injury_table(
    url: str,
    status: str,
    *,
    enrich_player_names_from_profiles: bool = True,
    max_profile_fetches: int = 300,
    per_profile_sleep_seconds: float = 0.2,
) -> list[InjuryReportRow]:
    html = fetch_html(url)
    return parse_injury_table_html(
        html,
        url=url,
        status=status,
        enrich_player_names_from_profiles=enrich_player_names_from_profiles,
        max_profile_fetches=max_profile_fetches,
        per_profile_sleep_seconds=per_profile_sleep_seconds,
    )


def parse_injury_table_html(
    html: str,
    *,
    url: str,
    status: str,
    enrich_player_names_from_profiles: bool = True,
    max_profile_fetches: int = 300,
    per_profile_sleep_seconds: float = 0.2,
) -> list[InjuryReportRow]:
    """
    Parse TennisExplorer injury list HTML into structured rows.

    These pages often abbreviate first names (e.g. "Gaston H."), so by default we
    "enrich" the player name by fetching the player's profile page and extracting
    the full name from <h1>/<title>.
    """
    if status not in ("injured", "returning"):
        raise ValueError("status must be 'injured' or 'returning'")

    soup = BeautifulSoup(html, "lxml")

    # Find the first table that contains a "Start" column.
    tables = soup.find_all("table")
    target_table = None
    for t in tables:
        header_cells = [normalize_player_name(th.get_text(" ", strip=True)).lower() for th in t.find_all("th")]
        if any(h in ("start", "date of return") for h in header_cells):
            target_table = t
            break
    if target_table is None:
        raise ValueError("Could not find injury table on TennisExplorer page")

    profile_cache: dict[str, Optional[str]] = {}
    profile_fetches = 0

    out: list[InjuryReportRow] = []
    for tr in target_table.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue

        start_txt = normalize_player_name(tds[0].get_text(" ", strip=True))
        name_cell = tds[1]
        name_txt = normalize_player_name(name_cell.get_text(" ", strip=True))
        if not name_txt:
            continue

        a = name_cell.find("a")
        href = a.get("href") if a else None
        profile_url = None
        if href:
            profile_url = href if href.startswith("http") else f"{TENNISEXPLORER_BASE}{href}"

        tournament_txt = normalize_player_name(tds[2].get_text(" ", strip=True)) if len(tds) >= 3 else None
        reason_txt = normalize_player_name(tds[3].get_text(" ", strip=True)) if len(tds) >= 4 else None

        # Enrich abbreviated names by visiting the player profile
        enriched_name = None
        needs_enrich = bool(re.search(r"\b[A-Z]\.$", name_txt)) or name_txt.endswith(".")
        if (
            enrich_player_names_from_profiles
            and needs_enrich
            and profile_url
            and profile_fetches < max_profile_fetches
        ):
            if profile_url in profile_cache:
                enriched_name = profile_cache[profile_url]
            else:
                profile_html = fetch_html(profile_url)
                enriched_name = _extract_player_display_name_from_profile_html(profile_html)
                profile_cache[profile_url] = enriched_name
                profile_fetches += 1
                if per_profile_sleep_seconds:
                    import time

                    time.sleep(per_profile_sleep_seconds)

        final_name = normalize_player_name(enriched_name or name_txt)
        out.append(
            InjuryReportRow(
                status=status,
                start_date=_parse_ddmmyyyy(start_txt),
                player_name=final_name,
                player_name_norm=to_name_key(final_name),
                player_profile_url=profile_url,
                tournament=tournament_txt or None,
                reason=reason_txt or None,
                source_url=url,
            )
        )

    if not out:
        raise ValueError("Parsed 0 injury rows; page format likely changed")
    return out


def scrape_injuries(
    *,
    enrich_player_names_from_profiles: bool = True,
    max_profile_fetches: int = 300,
    per_profile_sleep_seconds: float = 0.2,
) -> list[InjuryReportRow]:
    injured = scrape_injury_table(
        INJURED_URL,
        "injured",
        enrich_player_names_from_profiles=enrich_player_names_from_profiles,
        max_profile_fetches=max_profile_fetches,
        per_profile_sleep_seconds=per_profile_sleep_seconds,
    )
    returning = scrape_injury_table(
        RETURNING_URL,
        "returning",
        enrich_player_names_from_profiles=enrich_player_names_from_profiles,
        max_profile_fetches=max_profile_fetches,
        per_profile_sleep_seconds=per_profile_sleep_seconds,
    )
    return injured + returning


