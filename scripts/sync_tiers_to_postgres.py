#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import text

# Ensure we can import from src/ when running as a script
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from tennis_simulator.db.connection import get_engine  # noqa: E402
from tennis_simulator.db.tiers import ensure_tier_tables, create_tier_set, upsert_tiers  # noqa: E402


def normalize_player_name(name: str) -> str:
    # Keep this logic consistent with the scraper normalizer (NBSP, whitespace, etc.)
    if name is None:
        return ""
    s = str(name).replace("\u00A0", " ")
    s = " ".join(s.split())
    return s.strip()


def _load_module_from_path(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    if not spec or not spec.loader:
        raise RuntimeError(f"Could not load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def _extract_players(mod: Any, list_name: str) -> list[dict]:
    players = getattr(mod, list_name)
    out = []
    for p in players:
        name = normalize_player_name(getattr(p, "name"))
        tier = getattr(p, "tier").value if hasattr(getattr(p, "tier"), "value") else str(getattr(p, "tier"))
        out.append({"name": name, "tier": tier})
    return out


def main():
    ap = argparse.ArgumentParser(description="Sync Scorito tiers from data/import/*.py into Postgres.")
    ap.add_argument("--men-file", default="data/import/men_database.py")
    ap.add_argument("--women-file", default="data/import/women_database.py")
    ap.add_argument("--tier-set-name", default="initial_from_import_files")
    ap.add_argument("--tournament", default=None)
    ap.add_argument("--year", type=int, default=None)
    ap.add_argument("--make-active", action="store_true", default=True)
    args = ap.parse_args()

    engine = get_engine()
    ensure_tier_tables(engine)

    men_mod = _load_module_from_path(Path(args.men_file), "men_database_import")
    women_mod = _load_module_from_path(Path(args.women_file), "women_database_import")

    men_players = _extract_players(men_mod, "MEN_PLAYERS")
    women_players = _extract_players(women_mod, "WOMEN_PLAYERS")

    # Ensure tennis.players exists (created by dagster) and populate missing players.
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS tennis"))

    for gender, players in (("men", men_players), ("women", women_players)):
        tier_set_id = create_tier_set(
            engine,
            name=args.tier_set_name,
            gender=gender,
            tournament=args.tournament,
            year=args.year,
            make_active=bool(args.make_active),
        )
        mapping = {p["name"]: p["tier"] for p in players}
        upsert_tiers(engine, tier_set_id=tier_set_id, gender=gender, tiers=mapping)
        print(f"Synced {len(mapping)} {gender} tiers into tier_set_id={tier_set_id}")


if __name__ == "__main__":
    main()


