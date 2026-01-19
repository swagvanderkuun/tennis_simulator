#!/usr/bin/env python3
"""
Streamlit Dashboard for Tennis Simulator
Fast version using static database
"""

import streamlit as st
import pandas as pd
import numpy as np
import re
import sys
import os
from typing import Dict, List, Optional
import random
import plotly.graph_objects as go
from sqlalchemy import text
from collections import defaultdict

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tennis_simulator.core.models import Player, Tier
from tennis_simulator.simulators.elo_match_simulator import EloMatchSimulator, EloWeights, create_match_simulator
from tennis_simulator.data.static_database import populate_static_database  # legacy fallback
from tennis_simulator.simulators.fixed_draw_elo_simulator import FixedDrawEloSimulator  # legacy fallback
from tennis_simulator.db.connection import get_engine
from tennis_simulator.db.tiers import (
    ensure_tier_tables,
    list_tier_sets,
    get_active_tier_set_id,
    set_active_tier_set,
    create_tier_set,
    copy_tier_set,
    load_tiers,
    upsert_tiers,
    ensure_tier_set_has_all_elo_current_players,
    TIERS,
)

import importlib.util
from pathlib import Path


# Page configuration
st.set_page_config(
    page_title="Tennis Simulator Dashboard",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .player-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ---- Global simulator weight presets (must sum to 1.0) ----
WEIGHT_PRESETS: dict[str, EloWeights] = {
    "Custom (use sliders)": EloWeights(),  # placeholder; actual value comes from sliders/global_weights
    "Overall (default)": EloWeights(elo_weight=0.45, helo_weight=0.25, celo_weight=0.20, gelo_weight=0.10),
    "Elo only": EloWeights(
        elo_weight=1.0,
        helo_weight=0.0,
        celo_weight=0.0,
        gelo_weight=0.0,
        form_elo_scale=0.0,
        form_elo_cap=0.0,
    ),
    "Hard Court Focus": EloWeights(elo_weight=0.25, helo_weight=0.50, celo_weight=0.15, gelo_weight=0.10),
    "Clay Court Focus": EloWeights(elo_weight=0.25, helo_weight=0.15, celo_weight=0.50, gelo_weight=0.10),
    "Grass Court Focus": EloWeights(elo_weight=0.25, helo_weight=0.15, celo_weight=0.10, gelo_weight=0.50),
}


def _weights_sig(weights: EloWeights) -> tuple[float, float, float, float, float, float]:
    return (
        float(weights.elo_weight),
        float(weights.helo_weight),
        float(weights.celo_weight),
        float(weights.gelo_weight),
        float(weights.form_elo_scale),
        float(weights.form_elo_cap),
    )


def _apply_weights(weights: EloWeights, *, set_slider_keys: bool) -> None:
    """
    Force-set both the slider widget state and the global weights object.
    This makes presets actually apply immediately in Streamlit (slider keys keep their state).
    """
    st.session_state.global_weights = weights
    st.session_state["_weights_sliders_sig"] = _weights_sig(weights)

    # IMPORTANT: Only write slider keys in contexts where those widgets haven't been created yet
    # in the current run (e.g., via on_click callback).
    if set_slider_keys:
        st.session_state["elo_weight"] = float(weights.elo_weight)
        st.session_state["helo_weight"] = float(weights.helo_weight)
        st.session_state["celo_weight"] = float(weights.celo_weight)
        st.session_state["gelo_weight"] = float(weights.gelo_weight)
        st.session_state["form_elo_scale_slider"] = float(weights.form_elo_scale)
        st.session_state["form_elo_cap_slider"] = float(weights.form_elo_cap)


def _apply_preset(preset_name: str, *, set_slider_keys: bool) -> None:
    w = WEIGHT_PRESETS[preset_name]
    st.session_state["active_preset"] = preset_name
    _apply_weights(w, set_slider_keys=set_slider_keys)


def _weights_selector(label: str, key: str) -> EloWeights:
    """
    Show a preset selector and return the currently active weights.
    Selecting a preset overwrites the global weights used throughout the app.
    """
    options = list(WEIGHT_PRESETS.keys())
    selected = st.selectbox(label, options=options, key=key)
    if selected != "Custom (use sliders)":
        w = WEIGHT_PRESETS[selected]
        # Apply globally (do NOT touch slider keys here; those may exist on other pages).
        _apply_preset(selected, set_slider_keys=False)
        return w

    # Custom: use global weights if present, otherwise defaults
    return st.session_state.global_weights if "global_weights" in st.session_state else EloWeights()


@st.cache_data
def load_static_database(gender: str) -> Dict[str, any]:
    """Load static database with caching for performance"""
    try:
        db = populate_static_database(gender)
        return db
    except Exception as e:
        st.error(f"Error loading {gender} database: {e}")
        return {}

@st.cache_resource
def get_cached_engine():
    return get_engine()


def ensure_elo_current_form_columns(engine) -> None:
    """
    Safety migration for the dashboard container: ensure the precomputed form columns exist.
    Dagster also runs similar additive migrations, but the dashboard may start up before Dagster.
    """
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS tennis"))
        conn.execute(text("ALTER TABLE tennis.elo_current ADD COLUMN IF NOT EXISTS elo_4w double precision"))
        conn.execute(text("ALTER TABLE tennis.elo_current ADD COLUMN IF NOT EXISTS elo_12w double precision"))
        conn.execute(text("ALTER TABLE tennis.elo_current ADD COLUMN IF NOT EXISTS form_4w double precision"))
        conn.execute(text("ALTER TABLE tennis.elo_current ADD COLUMN IF NOT EXISTS form_12w double precision"))
        conn.execute(text("ALTER TABLE tennis.elo_current ADD COLUMN IF NOT EXISTS form double precision"))


@st.cache_data(ttl=300)
def load_postgres_players_df(gender: str) -> pd.DataFrame:
    """
    Load the *current* ratings + active tier assignment from Postgres.
    Uses:
      - tennis.elo_current (latest overwritten)
      - tennis.tier_sets (active=1)
      - tennis.tier_assignments
    """
    engine = get_cached_engine()
    ensure_tier_tables(engine)
    ensure_elo_current_form_columns(engine)

    # NOTE: form is precomputed in Postgres (tennis.elo_current.form*) by the ETL pipeline.
    # This avoids per-player LATERAL joins and makes the dashboard much faster.
    sql = text(
        """
        WITH active_set AS (
          SELECT id
          FROM tennis.tier_sets
          WHERE gender = :gender AND active = 1
          ORDER BY created_at DESC, id DESC
          LIMIT 1
        )
        SELECT
          c.player_name AS name,
          COALESCE(ta.tier, 'D') AS tier,
          c.elo,
          c.helo,
          c.celo,
          c.gelo,
          c.rank AS ranking,
          c.elo_rank,
          c.as_of,
          c.elo_4w,
          c.elo_12w,
          COALESCE(
            c.form,
            0.75 * COALESCE(c.form_4w, 0.0) + 0.25 * COALESCE(c.form_12w, 0.0),
            0.0
          ) AS form
        FROM tennis.elo_current c
        LEFT JOIN active_set s ON true
        LEFT JOIN tennis.tier_assignments ta
          ON ta.tier_set_id = s.id AND ta.player_id = c.player_id
        WHERE c.gender = :gender
        ORDER BY c.elo_rank NULLS LAST, c.player_name
        """
    )
    with engine.begin() as conn:
        rows = conn.execute(sql, {"gender": gender}).mappings().all()
    return pd.DataFrame(rows)


def load_database_df(gender: str) -> pd.DataFrame:
    """
    Preferred: Postgres. Fallback: legacy file-based static database.
    """
    try:
        df = load_postgres_players_df(gender)
        if df.empty:
            st.warning("Postgres returned 0 players; falling back to legacy static database.")
            raise RuntimeError("empty postgres dataset")
        return df
    except Exception as e:
        st.warning(f"Using legacy file-based database for {gender} (Postgres not available): {e}")
        db = load_static_database(gender)
        if not db:
            return pd.DataFrame()
        rows = []
        for name, data in db.items():
            rows.append(
                {
                    "name": name,
                    "tier": data.tier,
                    "elo": data.elo,
                    "helo": data.helo,
                    "celo": data.celo,
                    "gelo": data.gelo,
                    "ranking": data.ranking if hasattr(data, "ranking") else None,
                    "elo_rank": None,
                    "as_of": None,
                    "form": data.form if hasattr(data, "form") else None,
                }
            )
        return pd.DataFrame(rows)


def create_player_from_static_data(name: str, data: any) -> Player:
    """Create Player object from static database data"""
    player = Player(
        name=name,
        country="N/A",  # Static DB doesn't have country
        seeding=None,
        tier=Tier(data.tier),
        elo=data.elo,
        helo=data.helo,
        celo=data.celo,
        gelo=data.gelo,
        atp_rank=data.ranking if hasattr(data, 'ranking') else None,
        wta_rank=data.ranking if hasattr(data, 'ranking') else None
    )
    
    # Add form attribute if available
    if hasattr(data, 'form'):
        player.form = data.form
    
    return player


def display_database_overview(db: Dict[str, any], gender: str):
    """Display database overview with statistics"""
    st.subheader(f"📊 {gender.title()} Database Overview")
    
    # Convert to DataFrame for easier analysis
    players_data = []
    for name, data in db.items():
        players_data.append({
            'Name': name,
            'Tier': data.tier,
            'Elo': data.elo,
            'hElo': data.helo,
            'cElo': data.celo,
            'gElo': data.gelo,
            'Form': data.form if hasattr(data, 'form') else None,
            'Ranking': data.ranking if hasattr(data, 'ranking') else None
        })
    
    df = pd.DataFrame(players_data)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Players", len(df))
    
    with col2:
        tier_counts = df['Tier'].value_counts()
        st.metric("Tier A Players", tier_counts.get('A', 0))
    
    with col3:
        st.metric("Tier B Players", tier_counts.get('B', 0))
    
    with col4:
        st.metric("Tier C Players", tier_counts.get('C', 0))
    
    # Tier distribution
    st.subheader("Tier Distribution")
    tier_chart = df['Tier'].value_counts().sort_index()
    st.bar_chart(tier_chart)
    
    # Elo distribution
    st.subheader("Elo Rating Distribution")
    if not df['Elo'].isna().all():
        # Create histogram data using pandas
        elo_data = df['Elo'].dropna()
        if len(elo_data) > 0:
            # Create histogram bins and convert to string labels
            bins = pd.cut(elo_data, bins=20)
            hist_data = bins.value_counts().sort_index()
            # Convert interval index to string labels
            hist_data.index = [str(interval) for interval in hist_data.index]
            st.bar_chart(hist_data)
    
    return df


def display_database_overview_from_df(df: pd.DataFrame, gender: str):
    st.subheader(f"📊 {gender.title()} Database Overview")
    if df.empty:
        st.error("No data available.")
        return df

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Players", len(df))
    with col2:
        st.metric("Tier A Players", int((df["tier"] == "A").sum()))
    with col3:
        st.metric("Tier B Players", int((df["tier"] == "B").sum()))
    with col4:
        st.metric("Tier C Players", int((df["tier"] == "C").sum()))

    st.subheader("Tier Distribution")
    st.bar_chart(df["tier"].value_counts().sort_index())

    st.subheader("Elo Rating Distribution")
    if df["elo"].notna().any():
        elo_data = df["elo"].dropna()
        if len(elo_data) > 0:
            bins = pd.cut(elo_data, bins=20)
            hist_data = bins.value_counts().sort_index()
            hist_data.index = [str(interval) for interval in hist_data.index]
            st.bar_chart(hist_data)
    
    return df


def display_player_search(df: pd.DataFrame):
    """Display player search functionality"""
    st.subheader("🔍 Player Search")
    
    # Search by name
    search_term = st.text_input("Search by player name:", placeholder="Enter player name...")
    
    if search_term:
        filtered_df = df[df['Name'].str.contains(search_term, case=False, na=False)]
        if not filtered_df.empty:
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.info("No players found matching your search.")
    
    # Filter by tier
    st.subheader("Filter by Tier")
    selected_tiers = st.multiselect(
        "Select tiers to display:",
        options=['A', 'B', 'C', 'D'],
        default=['A', 'B']
    )
    
    if selected_tiers:
        tier_filtered_df = df[df['Tier'].isin(selected_tiers)]
        # Optional sort
        sort_options = [c for c in ["Elo Rank", "Elo", "Form", "Form Rank", "Ranking", "Name"] if c in tier_filtered_df.columns]
        sort_by = st.selectbox("Sort by:", options=sort_options or ["Name"])
        ascending = st.checkbox("Ascending", value=False)
        if sort_by in tier_filtered_df.columns:
            tier_filtered_df = tier_filtered_df.sort_values(by=sort_by, ascending=ascending, na_position="last")
        st.dataframe(tier_filtered_df, use_container_width=True)


def display_match_simulation(db: Dict[str, any], gender: str = 'women'):
    """Display match simulation interface"""
    st.subheader("🎾 Match Simulation")
    
    # Check if global weights are available
    weights = _weights_selector("Preset (Match Simulation):", key=f"preset_match_sim_{gender}")
    simulator = EloMatchSimulator(weights=weights)
    st.info(f"Using weights: total=1.0, form_scale={weights.form_elo_scale:.1f}, form_cap={weights.form_elo_cap:.1f}")
    
    # Show gender-specific information
    if gender == 'men':
        st.info("🏆 Men's matches use best-of-5 sets (five-set probability adjustment applied)")
    else:
        st.info("🏆 Women's matches use best-of-3 sets (standard probability calculation)")
    
    # Player selection
    # db is either legacy dict or a DataFrame-like dict mapping; handle both
    player_names = list(db.keys()) if isinstance(db, dict) else []
    
    col1, col2 = st.columns(2)
    
    with col1:
        player1_name = st.selectbox("Select Player 1:", player_names, key="player1")
    
    with col2:
        player2_name = st.selectbox("Select Player 2:", player_names, key="player2")
    
    if player1_name and player2_name and player1_name != player2_name:
        # Create player objects
        player1_data = db[player1_name]
        player2_data = db[player2_name]
        
        player1 = create_player_from_static_data(player1_name, player1_data)
        player2 = create_player_from_static_data(player2_name, player2_data)
        
        # Display player comparison
        st.subheader("Player Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**{player1.name}**")
            st.markdown(f"Tier: {player1.tier.value}")
            st.markdown(f"Elo: {player1.elo:.1f}")
            st.markdown(f"hElo: {player1.helo:.1f}")
            st.markdown(f"cElo: {player1.celo:.1f}")
            st.markdown(f"gElo: {player1.gelo:.1f}")
            st.markdown(f"Form: {player1.form:.1f}" if hasattr(player1, 'form') and player1.form is not None else "Form: N/A")
        
        with col2:
            st.markdown(f"**{player2.name}**")
            st.markdown(f"Tier: {player2.tier.value}")
            st.markdown(f"Elo: {player2.elo:.1f}")
            st.markdown(f"hElo: {player2.helo:.1f}")
            st.markdown(f"cElo: {player2.celo:.1f}")
            st.markdown(f"gElo: {player2.gelo:.1f}")
            st.markdown(f"Form: {player2.form:.1f}" if hasattr(player2, 'form') and player2.form is not None else "Form: N/A")
        
        # Calculate win probability
        win_prob = simulator.calculate_win_probability(player1, player2, gender)
        
        st.subheader("Match Prediction")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(f"{player1.name} Win Probability", f"{win_prob:.1%}")
        
        with col2:
            st.metric(f"{player2.name} Win Probability", f"{1-win_prob:.1%}")
        
        with col3:
            rating_diff = simulator.calculate_weighted_rating(player2) - simulator.calculate_weighted_rating(player1)
            st.metric("Rating Difference", f"{rating_diff:.1f}")
        
        # Simulate match button
        if st.button("🎯 Simulate Match", type="primary"):
            winner, loser, details = simulator.simulate_match(player1, player2, gender)
            
            st.success(f"🏆 **Winner: {winner.name}**")
            st.info(f"Runner-up: {loser.name}")
            
            # Show match details
            with st.expander("Match Details"):
                st.json(details)
        
        # Multiple simulations
        st.subheader("📈 Multiple Simulations")
        
        num_simulations = st.slider("Number of simulations:", 10, 1000, 100, 10)
        
        if st.button("🔄 Run Multiple Simulations"):
            with st.spinner(f"Running {num_simulations} simulations..."):
                player1_wins = 0
                results = []
                
                for i in range(num_simulations):
                    winner, _, _ = simulator.simulate_match(player1, player2, gender)
                    if winner.name == player1.name:
                        player1_wins += 1
                    results.append(winner.name)
                
                win_rate = player1_wins / num_simulations
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(f"{player1.name} Wins", f"{player1_wins}/{num_simulations}")
                    st.metric("Win Rate", f"{win_rate:.1%}")
                
                with col2:
                    st.metric(f"{player2.name} Wins", f"{num_simulations-player1_wins}/{num_simulations}")
                    st.metric("Win Rate", f"{1-win_rate:.1%}")
                
                # Results distribution
                st.subheader("Simulation Results Distribution")
                results_df = pd.DataFrame(results, columns=['Winner'])
                winner_counts = results_df['Winner'].value_counts()
                st.bar_chart(winner_counts)


def create_player_from_row(row: dict, gender: str) -> Player:
    def _num_or_none(v):
        # pandas may give NaN for SQL NULLs; simulator must see None not NaN
        try:
            if v is None:
                return None
            if isinstance(v, (float, np.floating)) and (np.isnan(v) or np.isinf(v)):
                return None
            return float(v)
        except Exception:
            return None

    p = Player(
        name=row["name"],
        country="N/A",
        seeding=None,
        tier=Tier(row["tier"]),
        elo=_num_or_none(row.get("elo")),
        helo=_num_or_none(row.get("helo")),
        celo=_num_or_none(row.get("celo")),
        gelo=_num_or_none(row.get("gelo")),
        atp_rank=row.get("ranking") if gender == "men" else None,
        wta_rank=row.get("ranking") if gender == "women" else None,
    )
    # `form` is derived from Elo deltas over time (Elo points), see load_postgres_players_df().
    p.form = _num_or_none(row.get("form")) or 0.0
    return p


def display_match_simulation_from_df(df: pd.DataFrame, gender: str):
    st.subheader("🎾 Match Simulation")

    if df.empty:
        st.error("No player data available.")
        return

    weights = _weights_selector("Preset (Match Simulation):", key=f"preset_match_sim_df_{gender}")
    simulator = EloMatchSimulator(weights=weights)

    player_names = df["name"].tolist()

    col1, col2 = st.columns(2)
    with col1:
        p1_name = st.selectbox("Select Player 1:", player_names, key=f"db_p1_{gender}")
    with col2:
        p2_name = st.selectbox("Select Player 2:", player_names, key=f"db_p2_{gender}")

    if p1_name == p2_name:
        st.info("Choose two different players.")
        return

    r1 = df[df["name"] == p1_name].iloc[0].to_dict()
    r2 = df[df["name"] == p2_name].iloc[0].to_dict()

    player1 = create_player_from_row(r1, gender)
    player2 = create_player_from_row(r2, gender)

    win_prob = simulator.calculate_win_probability(player1, player2, gender)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"{player1.name} Win Probability", f"{win_prob:.1%}")
    with col2:
        st.metric(f"{player2.name} Win Probability", f"{1-win_prob:.1%}")
    with col3:
        rating_diff = simulator.calculate_weighted_rating(player2) - simulator.calculate_weighted_rating(player1)
        st.metric("Rating Difference", f"{rating_diff:.1f}")

    if st.button("🎯 Simulate Match", type="primary", key=f"db_sim_btn_{gender}"):
        winner, loser, details = simulator.simulate_match(player1, player2, gender)
        st.success(f"🏆 **Winner: {winner.name}**")
        st.info(f"Runner-up: {loser.name}")
        with st.expander("Match Details"):
            st.json(details)


@st.cache_data(ttl=300)
def list_draw_sources(tour: str) -> list[dict]:
    engine = get_cached_engine()
    with engine.begin() as conn:
        rows = conn.execute(
            text(
                """
                SELECT id, tournament_name, season_year, source_url
                FROM tennis.draw_sources
                WHERE tour = :tour AND active = 1
                ORDER BY season_year DESC, tournament_name ASC
                """
            ),
            {"tour": tour},
        ).mappings().all()
    return [dict(r) for r in rows]


@st.cache_data(ttl=300)
def get_latest_draw_snapshot_id(source_id: int) -> int | None:
    engine = get_cached_engine()
    with engine.begin() as conn:
        sid = conn.execute(
            text(
                """
                SELECT id
                FROM tennis.draw_snapshots
                WHERE source_id = :sid AND status='success'
                ORDER BY scraped_at DESC, id DESC
                LIMIT 1
                """
            ),
            {"sid": source_id},
        ).scalar_one_or_none()
    return int(sid) if sid is not None else None


@st.cache_data(ttl=300)
def load_draw_entries(snapshot_id: int) -> list[dict]:
    engine = get_cached_engine()
    with engine.begin() as conn:
        rows = conn.execute(
            text(
                """
                SELECT part_index, slot_index, seed_text, player_name, is_bye
                FROM tennis.draw_entries
                WHERE snapshot_id = :snapshot_id
                ORDER BY part_index, slot_index
                """
            ),
            {"snapshot_id": snapshot_id},
        ).mappings().all()
    return [dict(r) for r in rows]


@st.cache_data(ttl=300)
def load_draw_match_nodes(snapshot_id: int) -> list[dict]:
    """
    Load draw matches joined with leaf entries (for leaf round only).
    Non-leaf matches will have NULL entry columns and instead child_match ids.
    """
    engine = get_cached_engine()
    with engine.begin() as conn:
        rows = conn.execute(
            text(
                """
                SELECT
                  m.id,
                  m.round,
                  m.match_index,
                  m.child_match1_id,
                  m.child_match2_id,
                  e1.player_name AS p1_name,
                  e1.is_bye AS p1_bye,
                  e2.player_name AS p2_name,
                  e2.is_bye AS p2_bye
                FROM tennis.draw_matches m
                LEFT JOIN tennis.draw_entries e1 ON e1.id = m.entry1_id
                LEFT JOIN tennis.draw_entries e2 ON e2.id = m.entry2_id
                WHERE m.snapshot_id = :snapshot_id
                """
            ),
            {"snapshot_id": snapshot_id},
        ).mappings().all()
    return [dict(r) for r in rows]


def _get_default_scorito_scoring():
    # Fallback when scoring.txt isn't present on the server
    header = ["R1", "R2", "R3", "R4", "QF", "SF", "F"]
    scoring = {tier: [0 for _ in header] for tier in ["A", "B", "C", "D"]}
    return scoring, header


def _round_stage_mapping(rounds: set[str]) -> dict[str, str]:
    """
    Map DB round labels (R128/R64/R32/R16/QF/SF/F) to Scorito stages (R1..R4,QF,SF,F).
    This is exact for 128-draw slams; for smaller draws it still maps sequentially.
    """
    mapping: dict[str, str] = {}
    numeric = []
    for r in rounds:
        if r.startswith("R"):
            try:
                numeric.append(int(r[1:]))
            except ValueError:
                pass
    numeric = sorted(set(numeric), reverse=True)  # leaf round first
    stage_prefix = ["R1", "R2", "R3", "R4"]
    for i, n in enumerate(numeric[:4]):
        mapping[f"R{n}"] = stage_prefix[i]

    # Fixed late rounds
    if "QF" in rounds:
        mapping["QF"] = "QF"
    if "SF" in rounds:
        mapping["SF"] = "SF"
    if "F" in rounds:
        mapping["F"] = "F"
    return mapping


def _simulate_draw_tree_once(
    *,
    df_players: pd.DataFrame,
    gender: str,
    snapshot_id: int,
    simulator: EloMatchSimulator,
    track_rounds: bool = False,
):
    """
    Simulate a full bracket from draw_matches tree.
    Returns (winner_name, bracket_tree, reached_stage_by_player, match_results).
    `match_results` is a list of dicts: {"stage": "R1"/.../"F", "round": "R128"/.../"F", "winner": str, "loser": str}
    """
    nodes = load_draw_match_nodes(snapshot_id)
    if not nodes:
        raise RuntimeError("No draw matches found for snapshot")

    by_id = {n["id"]: n for n in nodes}
    rounds = {n["round"] for n in nodes}
    stage_map = _round_stage_mapping(rounds)

    # Find root (final)
    finals = [n for n in nodes if n["round"] == "F"]
    if not finals:
        raise RuntimeError("No final match found in draw_matches for snapshot")
    root = sorted(finals, key=lambda x: x["match_index"])[0]

    # Player lookup
    row_map = {r["name"]: r for r in df_players.to_dict(orient="records")}

    reached_stage: dict[str, str] = {}
    match_results: list[dict] = []

    def note_reached(player_name: str, match_round: str):
        if not track_rounds:
            return
        stage = stage_map.get(match_round)
        if not stage:
            return
        order = ["R1", "R2", "R3", "R4", "QF", "SF", "F"]
        prev = reached_stage.get(player_name)
        if prev is None:
            reached_stage[player_name] = stage
            return
        if order.index(stage) > order.index(prev):
            reached_stage[player_name] = stage

    def get_player_row(name: str) -> dict:
        return row_map.get(
            name,
            {
                "name": name,
                "tier": "D",
                "elo": 1500,
                "helo": 1500,
                "celo": 1500,
                "gelo": 1500,
                "ranking": None,
                "form": 0.0,
            },
        )

    def simulate_match(p1_name: str, p1_bye: bool, p2_name: str, p2_bye: bool, match_round: str) -> tuple[str, dict]:
        # Track that both participants reached this match round
        if p1_name and not p1_bye:
            note_reached(p1_name, match_round)
        if p2_name and not p2_bye:
            note_reached(p2_name, match_round)

        if p1_bye and not p2_bye:
            return p2_name, {"name": match_round, "children": [{"name": "BYE", "children": []}, {"name": p2_name, "children": []}], "winner": p2_name}
        if p2_bye and not p1_bye:
            return p1_name, {"name": match_round, "children": [{"name": p1_name, "children": []}, {"name": "BYE", "children": []}], "winner": p1_name}

        pl1 = create_player_from_row(get_player_row(p1_name), gender)
        pl2 = create_player_from_row(get_player_row(p2_name), gender)
        winner, _, _ = simulator.simulate_match(pl1, pl2, gender)
        if track_rounds:
            stage = stage_map.get(match_round)
            if stage:
                loser_name = pl2.name if winner.name == pl1.name else pl1.name
                match_results.append(
                    {
                        "stage": stage,
                        "round": match_round,
                        "winner": winner.name,
                        "loser": loser_name,
                    }
                )
        tree = {"name": match_round, "children": [{"name": p1_name, "children": []}, {"name": p2_name, "children": []}], "winner": winner.name}
        return winner.name, tree

    def dfs(match_id: int) -> tuple[str, dict]:
        n = by_id[match_id]
        rnd = n["round"]
        # Leaf match: entries populated
        if n["child_match1_id"] is None and n["child_match2_id"] is None:
            p1_name = n["p1_name"] or ""
            p2_name = n["p2_name"] or ""
            p1_bye = bool(n["p1_bye"]) if n["p1_bye"] is not None else (str(p1_name).upper() == "BYE")
            p2_bye = bool(n["p2_bye"]) if n["p2_bye"] is not None else (str(p2_name).upper() == "BYE")
            winner_name, match_tree = simulate_match(p1_name, p1_bye, p2_name, p2_bye, rnd)
            match_tree["name"] = f"{rnd} #{n['match_index']}"
            return winner_name, match_tree

        # Non-leaf: winners of child matches
        w1, t1 = dfs(int(n["child_match1_id"]))
        w2, t2 = dfs(int(n["child_match2_id"]))

        note_reached(w1, rnd)
        note_reached(w2, rnd)

        pl1 = create_player_from_row(get_player_row(w1), gender)
        pl2 = create_player_from_row(get_player_row(w2), gender)
        winner, _, _ = simulator.simulate_match(pl1, pl2, gender)
        if track_rounds:
            stage = stage_map.get(rnd)
            if stage:
                loser_name = pl2.name if winner.name == pl1.name else pl1.name
                match_results.append(
                    {
                        "stage": stage,
                        "round": rnd,
                        "winner": winner.name,
                        "loser": loser_name,
                    }
                )
        tree = {"name": f"{rnd} #{n['match_index']}", "children": [t1, t2], "winner": winner.name}
        return winner.name, tree

    winner_name, bracket_tree = dfs(int(root["id"]))
    if track_rounds and winner_name:
        reached_stage[winner_name] = "F"  # at least final reached
    return winner_name, bracket_tree, reached_stage, match_results


def simulate_draw_multiple(df_players: pd.DataFrame, entries: list[dict], gender: str, num_simulations: int) -> dict:
    """
    Simulate a fixed draw bracket using the given entries ordering.
    BYE entries auto-advance.
    """
    # Prefer the globally selected weights (or defaults).
    match_simulator = EloMatchSimulator(
        weights=st.session_state.global_weights if "global_weights" in st.session_state else EloWeights()
    )

    # Map name -> row
    row_map = {r["name"]: r for r in df_players.to_dict(orient="records")}

    # Build ordered players list with BYE placeholders
    ordered = []
    for e in entries:
        if int(e["is_bye"]) == 1 or str(e["player_name"]).upper() == "BYE":
            ordered.append({"is_bye": True, "name": "BYE"})
        else:
            name = e["player_name"]
            row = row_map.get(name, {"name": name, "tier": "D", "elo": 1500, "helo": 1500, "celo": 1500, "gelo": 1500, "ranking": None, "form": 0.0})
            ordered.append({"is_bye": False, "row": row})

    def play_round(players_list: list[dict]) -> list[dict]:
        winners = []
        for i in range(0, len(players_list), 2):
            p1 = players_list[i]
            p2 = players_list[i + 1]
            if p1.get("is_bye"):
                winners.append(p2)
                continue
            if p2.get("is_bye"):
                winners.append(p1)
                continue
            pl1 = create_player_from_row(p1["row"], gender)
            pl2 = create_player_from_row(p2["row"], gender)
            winner, _, _ = match_simulator.simulate_match(pl1, pl2, gender)
            winners.append({"is_bye": False, "row": p1["row"] if winner.name == pl1.name else p2["row"]})
        return winners

    from collections import Counter
    winners_c = Counter()
    finalists_c = Counter()
    semifinalists_c = Counter()
    quarterfinalists_c = Counter()

    for _ in range(num_simulations):
        current = ordered
        # Track rounds by list length after each round
        while len(current) > 1:
            next_players = play_round(current)
            # If next round results in certain size, record those players as having reached that round
            # (Crude but useful: when list size is 4 => semifinalists, 2 => finalists, 1 => winner)
            if len(next_players) == 8:
                for p in next_players:
                    if not p.get("is_bye"):
                        quarterfinalists_c[p["row"]["name"]] += 1
            if len(next_players) == 4:
                for p in next_players:
                    if not p.get("is_bye"):
                        semifinalists_c[p["row"]["name"]] += 1
            if len(next_players) == 2:
                for p in next_players:
                    if not p.get("is_bye"):
                        finalists_c[p["row"]["name"]] += 1
            if len(next_players) == 1:
                p = next_players[0]
                if not p.get("is_bye"):
                    winners_c[p["row"]["name"]] += 1
            current = next_players

    return {
        "total_simulations": num_simulations,
        "winners": winners_c,
        "finalists": finalists_c,
        "semifinalists": semifinalists_c,
        "quarterfinalists": quarterfinalists_c,
    }


def display_elo_weights_config():
    """Display Elo weights configuration interface."""
    st.header('⚖️ Elo Weights Configuration')
    st.write('Configure the weights for different Elo rating types in match simulation.')
    
    # Ensure sliders reflect current global weights when arriving on this page.
    base_w = st.session_state.global_weights if "global_weights" in st.session_state else WEIGHT_PRESETS["Overall (default)"]
    sig = _weights_sig(base_w)
    if st.session_state.get("_weights_sliders_sig") != sig:
        # Safe here: this runs before any slider widgets are created in this function.
        st.session_state["elo_weight"] = float(base_w.elo_weight)
        st.session_state["helo_weight"] = float(base_w.helo_weight)
        st.session_state["celo_weight"] = float(base_w.celo_weight)
        st.session_state["gelo_weight"] = float(base_w.gelo_weight)
        st.session_state["form_elo_scale_slider"] = float(base_w.form_elo_scale)
        st.session_state["form_elo_cap_slider"] = float(base_w.form_elo_cap)
        st.session_state["_weights_sliders_sig"] = sig
    
    # Weight configuration
    st.subheader('Weight Configuration')
    st.write('Adjust the weights for each Elo type. Weights must sum to 1.0.')
    
    col1, col2 = st.columns(2)
    
    with col1:
        elo_weight = st.slider(
            'Overall Elo Weight',
            0.0,
            1.0,
            float(st.session_state.get("elo_weight", base_w.elo_weight)),
            0.05,
            key="elo_weight",
        )
        helo_weight = st.slider(
            'Hard Court Elo Weight',
            0.0,
            1.0,
            float(st.session_state.get("helo_weight", base_w.helo_weight)),
            0.05,
            key="helo_weight",
        )
        celo_weight = st.slider(
            'Clay Court Elo Weight',
            0.0,
            1.0,
            float(st.session_state.get("celo_weight", base_w.celo_weight)),
            0.05,
            key="celo_weight",
        )
    
    with col2:
        gelo_weight = st.slider(
            'Grass Court Elo Weight',
            0.0,
            1.0,
            float(st.session_state.get("gelo_weight", base_w.gelo_weight)),
            0.05,
            key="gelo_weight",
        )
        # yElo intentionally removed from simulation model (sparse early season).
    
    # Form configuration
    st.subheader('Form Configuration')
    st.write('Configure form-based probability calculation.')
    
    col1, col2 = st.columns(2)
    
    with col1:
        form_elo_scale = st.slider(
            'Form Elo Scale',
            0.0,
            400.0,
            float(st.session_state.get("form_elo_scale_slider", base_w.form_elo_scale)),
            10.0,
            help="Converts rank-based form signal into Elo points. Higher = form matters more.",
            key="form_elo_scale_slider",
        )
    
    with col2:
        form_elo_cap = st.slider(
            'Form Elo Cap',
            0.0,
            200.0,
            float(st.session_state.get("form_elo_cap_slider", base_w.form_elo_cap)),
            5.0,
            help="Caps the maximum Elo boost/penalty from form (prevents extreme effects).",
            key="form_elo_cap_slider",
        )
    
    # Calculate total weight
    total_weight = elo_weight + helo_weight + celo_weight + gelo_weight
    
    # Display total weight
    if abs(total_weight - 1.0) < 0.01:
        st.success(f'✅ Total Weight: {total_weight:.2f}')
        # Automatically save weights when they sum to 1.0
        weights = EloWeights(
            elo_weight=elo_weight,
            helo_weight=helo_weight,
            celo_weight=celo_weight,
            gelo_weight=gelo_weight,
            form_elo_scale=form_elo_scale,
            form_elo_cap=form_elo_cap,
        )
        st.session_state.global_weights = weights
        st.success('✅ Weights automatically saved! These weights will be used in all simulators.')
        st.info('💡 Changes are saved automatically when weights sum to 1.0. No need to click any buttons!')
    else:
        st.error(f'❌ Total Weight: {total_weight:.2f} (must be 1.0)')
        st.warning('Weights will be saved automatically when they sum to 1.0.')
    
    # Preset configurations
    st.subheader('Preset Configurations')
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button('Hard Court Focus', on_click=lambda: _apply_preset("Hard Court Focus", set_slider_keys=True)):
            pass
    
    with col2:
        if st.button('Clay Court Focus', on_click=lambda: _apply_preset("Clay Court Focus", set_slider_keys=True)):
            pass
    
    with col3:
        if st.button('Grass Court Focus', on_click=lambda: _apply_preset("Grass Court Focus", set_slider_keys=True)):
            pass

    # Show current weights if available
    if 'global_weights' in st.session_state:
        st.subheader('Current Global Weights')
        weights = st.session_state.global_weights
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Elo", f"{weights.elo_weight:.2f}")
            st.metric("Hard Elo", f"{weights.helo_weight:.2f}")
            st.metric("Clay Elo", f"{weights.celo_weight:.2f}")
        with col2:
            st.metric("Grass Elo", f"{weights.gelo_weight:.2f}")
        with col3:
            st.metric("Form Elo Scale", f"{weights.form_elo_scale:.1f}")
            st.metric("Form Elo Cap", f"{weights.form_elo_cap:.1f}")


def display_explorer():
    """Display the tournament explorer (multiple simulations)"""
    st.subheader("🔍 Tournament Explorer")
    st.markdown("Run multiple tournament simulations to explore win probabilities and outcomes.")

    gender = st.selectbox("Select Gender:", options=["men", "women"], format_func=lambda x: x.title(), key="explorer_gender")
    tour = "atp" if gender == "men" else "wta"
    weights = _weights_selector("Preset (Explorer):", key=f"preset_explorer_{gender}")
    # Ensure downstream tournament sims use the selected weights without touching slider widget keys.
    _apply_weights(weights, set_slider_keys=False)

    sources = list_draw_sources(tour)
    if not sources:
        st.error(f"No draw sources found in Postgres for tour={tour}. Run scrape_draw_job first.")
        return

    label_to_id = {f"{s['season_year']} {tour.upper()} {s['tournament_name']}": s["id"] for s in sources}
    selected = st.selectbox("Select tournament draw:", options=list(label_to_id.keys()), key=f"explorer_draw_source_{gender}")
    source_id = label_to_id[selected]
    snap_id = get_latest_draw_snapshot_id(source_id)
    if not snap_id:
        st.error("No successful draw snapshot found for this tournament.")
        return

    num_simulations = st.slider("Number of tournament simulations:", 10, 1000, 100, 10, key="explorer_sims")
    
    if st.button("Run Tournament Explorer", type="primary", key="explorer_btn"):
        with st.spinner("Running tournament explorer..."):
            df_players = load_database_df(gender)
            if df_players.empty:
                st.error("No player data available.")
                return

            entries = load_draw_entries(snap_id)
            stats = simulate_draw_multiple(df_players, entries, gender, num_simulations)

            st.success(f"Explored {num_simulations} tournaments for {gender.title()} using draw snapshot {snap_id}.")
            winners = stats["winners"]
            finalists = stats["finalists"]
            semis = stats["semifinalists"]
            qfs = stats["quarterfinalists"]

            def top_probs(counter, n=10):
                total = stats["total_simulations"]
                return [(k, v / total) for k, v in counter.most_common(n)]

            st.subheader("Win Probabilities (Top 10)")
            st.table(pd.DataFrame(top_probs(winners), columns=["Player", "Win Probability"]))

            st.subheader("Final Probabilities (Top 10)")
            st.table(pd.DataFrame(top_probs(finalists), columns=["Player", "Final Probability"]))

            st.subheader("Semifinal Probabilities (Top 10)")
            st.table(pd.DataFrame(top_probs(semis), columns=["Player", "Semifinal Probability"]))

            st.subheader("Quarterfinal Probabilities (Top 10)")
            st.table(pd.DataFrame(top_probs(qfs), columns=["Player", "Quarterfinal Probability"]))


def plot_bracket_tree(tree, x=0, y=0, x_spacing=200, y_spacing=30, level=0, positions=None, lines=None):
    """
    Recursively plot the bracket tree using Plotly. Returns node positions and lines for drawing.
    """
    if positions is None:
        positions = []
    if lines is None:
        lines = []
    # Calculate position for this node
    node_id = len(positions)
    positions.append({'x': x, 'y': y, 'label': tree['name'], 'winner': tree.get('winner', '')})
    # If leaf, return
    if not tree['children']:
        return positions, lines
    # For children, calculate y positions
    n = len(tree['children'])
    child_ys = []
    for i, child in enumerate(tree['children']):
        child_x = x + x_spacing
        child_y = y + (i - (n-1)/2) * y_spacing * (2 ** (5-level))
        child_ys.append(child_y)
        positions, lines = plot_bracket_tree(child, child_x, child_y, x_spacing, y_spacing, level+1, positions, lines)
        # Draw a line from this node to child
        lines.append({'x0': x, 'y0': y, 'x1': child_x, 'y1': child_y})
    return positions, lines


def display_single_tournament():
    st.header('🎾 Single Tournament Simulation')
    gender = st.radio('Select gender', ['men', 'women'], horizontal=True)
    df_players = load_database_df(gender)
    if df_players.empty:
        st.error("No player data available (Postgres).")
        return
    weights = _weights_selector("Preset (Single Tournament):", key=f"preset_single_tournament_{gender}")
    match_simulator = EloMatchSimulator(weights=weights)

    tour = "atp" if gender == "men" else "wta"
    sources = list_draw_sources(tour)
    if not sources:
        st.error(f"No draw sources found in Postgres for tour={tour}. Run scrape_draw_job first.")
        return
    label_to_id = {f"{s['season_year']} {tour.upper()} {s['tournament_name']}": s["id"] for s in sources}
    selected = st.selectbox("Select tournament draw:", options=list(label_to_id.keys()), key=f"single_tournament_source_{gender}")
    source_id = label_to_id[selected]
    snapshot_id = get_latest_draw_snapshot_id(source_id)
    if not snapshot_id:
        st.error("No successful draw snapshot found for this tournament.")
        return
    
    if st.button('Run Single Tournament Simulation'):
        winner, bracket_tree, _, _ = _simulate_draw_tree_once(
            df_players=df_players,
            gender=gender,
            snapshot_id=snapshot_id,
            simulator=match_simulator,
            track_rounds=False,
        )
        st.success(f'Winner: {winner or "?"}')
        positions, lines = plot_bracket_tree(bracket_tree)
        xs = [p['x'] for p in positions]
        ys = [p['y'] for p in positions]
        labels = [p['label'] for p in positions]
        winners = [p['winner'] for p in positions]
        fig = go.Figure()
        for line in lines:
            fig.add_shape(type='line', x0=line['x0'], y0=line['y0'], x1=line['x1'], y1=line['y1'], line=dict(color='gray', width=1))
        fig.add_trace(go.Scatter(x=xs, y=ys, mode='markers+text', text=labels, textposition='middle right', marker=dict(size=8, color='royalblue'), hovertext=winners, hoverinfo='text'))
        fig.update_layout(height=1200, width=1600, showlegend=False, margin=dict(l=20, r=20, t=40, b=20), xaxis=dict(showticklabels=False), yaxis=dict(showticklabels=False), plot_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info('Click "Run Single Tournament Simulation" to generate and view the bracket.')


def display_custom_weights():
    """Display custom weight configuration (legacy function - now redirects to global config)"""
    st.info("Elo weights are now configured globally. Please use the 'Elo Weights' tab to set weights that apply to all simulators.")
    
    # Show current global weights if available
    if 'global_weights' in st.session_state:
        st.subheader("Current Global Weights")
        weights = st.session_state.global_weights
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Overall Elo", f"{weights.elo_weight:.2f}")
            st.metric("Hard Elo", f"{weights.helo_weight:.2f}")
            st.metric("Clay Elo", f"{weights.celo_weight:.2f}")
        with col2:
            st.metric("Grass Elo", f"{weights.gelo_weight:.2f}")


def display_bracket_view():
    st.header('🎾 Bracket View')
    st.write('Visualize the full tournament bracket for a single simulation.')
    gender = st.radio('Select gender', ['men', 'women'], horizontal=True)
    if 'bracket_simulator' not in st.session_state:
        st.session_state['bracket_simulator'] = FixedDrawEloSimulator()
        st.session_state['bracket_simulator'].setup_tournaments()
    sim = st.session_state['bracket_simulator']
    if st.button('Run Single Simulation'):
        if gender == 'men':
            sim.simulate_tournament(sim.men_tournament)
            bracket_tree = sim.get_bracket_tree(sim.men_tournament)
            winner = sim.men_tournament.winner.name if sim.men_tournament.winner else '?'
        else:
            sim.simulate_tournament(sim.women_tournament)
            bracket_tree = sim.get_bracket_tree(sim.women_tournament)
            winner = sim.women_tournament.winner.name if sim.women_tournament.winner else '?'
        # Plot bracket
        positions, lines = plot_bracket_tree(bracket_tree)
        xs = [p['x'] for p in positions]
        ys = [p['y'] for p in positions]
        labels = [p['label'] for p in positions]
        winners = [p['winner'] for p in positions]
        fig = go.Figure()
        # Draw lines
        for line in lines:
            fig.add_shape(type='line', x0=line['x0'], y0=line['y0'], x1=line['x1'], y1=line['y1'], line=dict(color='gray', width=1))
        # Draw nodes
        fig.add_trace(go.Scatter(x=xs, y=ys, mode='markers+text', text=labels, textposition='middle right', marker=dict(size=8, color='royalblue'), hovertext=winners, hoverinfo='text'))
        fig.update_layout(height=1200, width=1600, showlegend=False, margin=dict(l=20, r=20, t=40, b=20), xaxis=dict(showticklabels=False), yaxis=dict(showticklabels=False), plot_bgcolor='white')
        st.plotly_chart(fig, use_container_width=True)
        st.success(f'Winner: {winner}')
    else:
        st.info('Click "Run Single Simulation" to generate and view the bracket.')


def parse_scorito_scoring(filepath='data/import/scoring.txt'):
    scoring = {}
    with open(filepath, 'r') as f:
        lines = f.readlines()
    header = lines[0].strip().split('\t')[1:]
    for line in lines[1:]:
        parts = line.strip().split('\t')
        tier = parts[0].upper()
        points = [int(x) for x in parts[1:]]
        scoring[tier] = points
    return scoring, header


def get_player_tier(player):
    # Player.tier is a Tier enum, get its value and uppercase
    return player.tier.value.upper()


def get_player_round_index(player):
    # Map round to index: R1=0, R2=1, ..., F=6
    round_map = {
        'R1': 0, 'R2': 1, 'R3': 2, 'R4': 3, 'QF': 4, 'SF': 5, 'F': 6
    }
    return round_map.get(player.current_round.value, 0)


def display_scorito_game_analysis():
    st.header('🎯 Scorito Game Analysis')
    num_simulations = st.number_input('Number of simulations', min_value=100, max_value=5000, value=1000, step=100)
    gender = st.radio('Select gender', ['men', 'women'], horizontal=True)
    df_players = load_database_df(gender)
    if df_players.empty:
        st.error("No player data available (Postgres).")
        return

    tour = "atp" if gender == "men" else "wta"
    sources = list_draw_sources(tour)
    if not sources:
        st.error(f"No draw sources found in Postgres for tour={tour}. Run scrape_draw_job first.")
        return
    label_to_id = {f"{s['season_year']} {tour.upper()} {s['tournament_name']}": s["id"] for s in sources}
    selected = st.selectbox("Select tournament draw:", options=list(label_to_id.keys()), key=f"scorito_source_{gender}")
    source_id = label_to_id[selected]
    snapshot_id = get_latest_draw_snapshot_id(source_id)
    if not snapshot_id:
        st.error("No successful draw snapshot found for this tournament.")
        return

    # Limit opponent stats to opponents the player can actually face in this bracket.
    # For each player, compute the set of possible opponents along their draw path
    # (union of sibling subtrees up to the final).
    _nodes = load_draw_match_nodes(snapshot_id)
    _by_id = {int(n["id"]): n for n in _nodes}
    _parent_of: dict[int, int] = {}
    for n in _nodes:
        pid = int(n["id"])
        c1 = n.get("child_match1_id")
        c2 = n.get("child_match2_id")
        if c1 is not None:
            _parent_of[int(c1)] = pid
        if c2 is not None:
            _parent_of[int(c2)] = pid

    _leaf_match_by_player: dict[str, int] = {}
    _leaf_set_cache: dict[int, set[str]] = {}

    def _leaf_players(match_id: int) -> set[str]:
        if match_id in _leaf_set_cache:
            return _leaf_set_cache[match_id]
        n = _by_id[match_id]
        c1 = n.get("child_match1_id")
        c2 = n.get("child_match2_id")
        if c1 is None and c2 is None:
            out: set[str] = set()
            for key_name, key_bye in (("p1_name", "p1_bye"), ("p2_name", "p2_bye")):
                nm = (n.get(key_name) or "").strip()
                if not nm:
                    continue
                is_bye = bool(n.get(key_bye)) if n.get(key_bye) is not None else (nm.upper() == "BYE")
                if is_bye or nm.upper() == "BYE":
                    continue
                out.add(nm)
                _leaf_match_by_player.setdefault(nm, match_id)
            _leaf_set_cache[match_id] = out
            return out
        out = set()
        if c1 is not None:
            out |= _leaf_players(int(c1))
        if c2 is not None:
            out |= _leaf_players(int(c2))
        _leaf_set_cache[match_id] = out
        return out

    _finals = [n for n in _nodes if str(n.get("round")) == "F"]
    _root_id = int(sorted(_finals, key=lambda x: x["match_index"])[0]["id"]) if _finals else int(_nodes[0]["id"])
    _leaf_players(_root_id)  # populate caches / leaf mapping

    possible_opponents_by_player: dict[str, set[str]] = {}
    for player_name, leaf_id in _leaf_match_by_player.items():
        poss: set[str] = set()
        cur = leaf_id
        while cur in _parent_of:
            parent = _parent_of[cur]
            pn = _by_id[parent]
            sib = None
            if pn.get("child_match1_id") is not None and int(pn["child_match1_id"]) == cur:
                sib = pn.get("child_match2_id")
            else:
                sib = pn.get("child_match1_id")
            if sib is not None:
                poss |= _leaf_players(int(sib))
            cur = parent
        poss.discard(player_name)
        possible_opponents_by_player[player_name] = poss

    # Scoring config: prefer file if present, otherwise editable default table
    scoring = None
    round_labels = None
    try:
        scoring, round_labels = parse_scorito_scoring()
    except Exception:
        scoring, round_labels = _get_default_scorito_scoring()
        st.warning("`data/import/scoring.txt` not found on server. Using editable default scoring (all zeros) below.")

    scoring_df = pd.DataFrame(
        [{"Tier": t, **{round_labels[i]: scoring[t][i] for i in range(len(round_labels))}} for t in ["A", "B", "C", "D"]]
    )
    scoring_df = st.data_editor(scoring_df, num_rows="fixed", use_container_width=True, key=f"scorito_scoring_{gender}")
    scoring = {row["Tier"]: [int(row[c]) for c in round_labels] for _, row in scoring_df.iterrows()}

    # Preset selector must be rendered unconditionally; otherwise changing it triggers a rerun
    # where the widget disappears (button returns False) and the selection can't persist.
    weights = _weights_selector("Preset (Scorito):", key=f"preset_scorito_{gender}")

    if st.button('Run Scorito Analysis'):
        with st.spinner(f'Running {num_simulations} simulations for Scorito analysis...'):
            match_sim = EloMatchSimulator(weights=weights)

            # Tier lookup from df_players (already includes active tier)
            tier_by_name = {r["name"]: r.get("tier", "D") for r in df_players.to_dict(orient="records")}

            # Points aggregation
            player_points: dict[str, list[int]] = defaultdict(list)
            stage_to_index = {lab: i for i, lab in enumerate(round_labels)}
            # Extra stats: elimination + most common opponents (eliminator / beaten)
            from collections import Counter as _Counter

            elim_idxs_by_player = defaultdict(list)  # name -> list[int] (elimination stage per simulation)
            elim_pair_by_player = defaultdict(_Counter)  # name -> Counter[(stage, eliminator)]
            beat_by_player = defaultdict(_Counter)  # name -> Counter[beaten_opponent]
            faced_by_player = defaultdict(_Counter)  # name -> Counter[opponent] (matches actually played)
            wins_by_player = defaultdict(_Counter)  # name -> Counter[opponent] (wins in matches played)
            faced_by_player_stage = defaultdict(lambda: defaultdict(_Counter))  # name -> stage -> Counter[opponent]
            wins_by_player_stage = defaultdict(lambda: defaultdict(_Counter))  # name -> stage -> Counter[opponent]

            for _ in range(num_simulations):
                winner, _, reached, match_results = _simulate_draw_tree_once(
                    df_players=df_players,
                    gender=gender,
                    snapshot_id=snapshot_id,
                    simulator=match_sim,
                    track_rounds=True,
                )

                # Winner: treat as reaching final (max label)
                # (Scoring file often doesn't have W; existing logic treated W as F.)
                if winner:
                    reached[winner] = "F"

                for name, stage in reached.items():
                    tier = str(tier_by_name.get(name, "D")).upper()
                    round_index = stage_to_index.get(stage, 0)
                    tier_scoring = scoring.get(tier, [0] * len(round_labels))
                    total_points = sum(tier_scoring[: round_index + 1]) if round_index >= 0 else 0
                    player_points[name].append(total_points)

                elim_stage_by_player: dict[str, str] = {}
                # match_results entries exist only for non-BYE matches
                for mr in match_results:
                    w_name = mr.get("winner")
                    l_name = mr.get("loser")
                    stage = mr.get("stage")
                    if not w_name or not l_name or not stage:
                        continue
                    beat_by_player[w_name][l_name] += 1
                    elim_pair_by_player[l_name][(stage, w_name)] += 1
                    elim_stage_by_player[l_name] = stage
                    # Track actual opponents played (symmetric) + wins
                    faced_by_player[w_name][l_name] += 1
                    faced_by_player[l_name][w_name] += 1
                    wins_by_player[w_name][l_name] += 1
                    faced_by_player_stage[w_name][stage][l_name] += 1
                    faced_by_player_stage[l_name][stage][w_name] += 1
                    wins_by_player_stage[w_name][stage][l_name] += 1

                # Ensure every reached player gets an elimination-stage entry for this simulation.
                # Winner: treat as reaching final.
                all_names = set(reached.keys())
                if winner:
                    all_names.add(winner)

                for name in all_names:
                    if winner and name == winner:
                        elim_stage = "F"
                    else:
                        elim_stage = elim_stage_by_player.get(name) or reached.get(name) or "R1"
                    elim_idx = int(stage_to_index.get(elim_stage, 0))
                    elim_idxs_by_player[name].append(elim_idx)

            avg_points = {name: (sum(pts) / len(pts) if pts else 0) for name, pts in player_points.items()}

            for tier in ['A', 'B', 'C', 'D']:
                st.subheader(f'Top 20 Players - Tier {tier}')
                tier_players = [(name, avg_points.get(name, 0)) for name, t in tier_by_name.items() if str(t).upper() == tier and name in avg_points]
                if tier_players:
                    tier_players.sort(key=lambda x: x[1], reverse=True)
                    top_20 = tier_players[:20]
                    # Name -> Elo lookup for opponent columns
                    elo_by_name = {r["name"]: r.get("elo") for r in df_players.to_dict(orient="records")}

                    def _round_label_from_idx(idx: int) -> str:
                        idx_i = int(idx)
                        idx_i = max(0, min(idx_i, len(round_labels) - 1))
                        return str(round_labels[idx_i])

                    data = []
                    from collections import Counter as _Counter
                    import numpy as _np

                    for name, points in top_20:
                        # Display name with current Elo rating (if known)
                        p_elo = elo_by_name.get(name)
                        if p_elo is not None and pd.notna(p_elo):
                            player_label = f"{name} ({float(p_elo):.0f})"
                        else:
                            player_label = name

                        # Elimination round stats
                        idxs = elim_idxs_by_player.get(name, [])
                        if idxs:
                            mean_idx = float(sum(idxs)) / float(len(idxs))
                            med_idx = int(_np.median(_np.array(idxs, dtype=float)))
                            mode_idx = int(_Counter(idxs).most_common(1)[0][0])
                            avg_elim = f"{_round_label_from_idx(int(round(mean_idx)))} ({mean_idx:.2f})"
                            median_elim = _round_label_from_idx(med_idx)
                            mode_elim = _round_label_from_idx(mode_idx)
                        else:
                            avg_elim = ""
                            median_elim = ""
                            mode_elim = ""

                        # Most common eliminator (joint with round)
                        elim_pair_counter = elim_pair_by_player.get(name)
                        if elim_pair_counter:
                            (elim_stage, eliminator), elim_times = elim_pair_counter.most_common(1)[0]
                            elim_rate = elim_times / float(num_simulations)
                            elim_stage_label = str(elim_stage)
                            eliminator_name = str(eliminator)
                        else:
                            elim_stage_label = ""
                            eliminator_name = ""
                            elim_rate = 0.0

                        # Opponents the player is likely to beat (based on simulated head-to-head when they actually face)
                        # win% = wins / matches_faced, where "matches faced" are only opponents the player
                        # actually played in the simulations (derived from match_results).
                        likely_beats_parts: list[str] = []
                        # We want <= 7 opponents (one per round). So for each stage, pick the opponent
                        # the player most often BEATS in that stage (across all simulations).
                        stage_order = list(round_labels)  # expected ["R1","R2","R3","R4","QF","SF","F"]
                        per_stage_faced = faced_by_player_stage.get(name) or {}
                        per_stage_wins = wins_by_player_stage.get(name) or {}

                        for stg in stage_order:
                            faced_ctr = per_stage_faced.get(stg) or _Counter()
                            if not faced_ctr:
                                continue
                            opp, faced = faced_ctr.most_common(1)[0]
                            faced_i = int(faced)
                            if not opp or faced_i <= 0:
                                continue

                            wins = int((per_stage_wins.get(stg) or _Counter()).get(opp, 0))
                            win_pct = wins / float(faced_i) if faced_i > 0 else 0.0

                            opp_elo = elo_by_name.get(opp)
                            opp_elo_str = f"{float(opp_elo):.0f}" if opp_elo is not None and pd.notna(opp_elo) else ""
                            label = f"{stg}: {opp} ({opp_elo_str}, {win_pct:.0%})" if opp_elo_str else f"{stg}: {opp} ({win_pct:.0%})"
                            likely_beats_parts.append(label)
                        likely_beats_str = ", ".join(likely_beats_parts)

                        data.append(
                            {
                                "Player": player_label,
                                "Avg Points": f"{points:.2f}",
                                "Avg Elim Round": avg_elim,
                                "Median Elim Round": median_elim,
                                "Mode Elim Round": mode_elim,
                                "Eliminated In": elim_stage_label,
                                "Eliminated By": eliminator_name,
                                "Elim Rate": f"{elim_rate:.1%}" if elim_rate else "0.0%",
                                "Likely Beats": likely_beats_str,
                            }
                        )
                    st.table(pd.DataFrame(data))
                else:
                    st.info(f'No players found in Tier {tier}')
    else:
        st.info('Click "Run Scorito Analysis" to simulate and analyze Scorito points.')


def _load_module_from_path(path: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Could not load module from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


def _normalize_name(name: str) -> str:
    if name is None:
        return ""
    s = str(name).replace("\u00A0", " ")
    s = " ".join(s.split())
    return s.strip()


def _extract_tiers_from_import_files(gender: str) -> dict[str, str]:
    if gender == "men":
        mod = _load_module_from_path("data/import/men_database.py", "men_database_import")
        players = getattr(mod, "MEN_PLAYERS")
    else:
        mod = _load_module_from_path("data/import/women_database.py", "women_database_import")
        players = getattr(mod, "WOMEN_PLAYERS")

    out: dict[str, str] = {}
    for p in players:
        name = _normalize_name(getattr(p, "name"))
        tier_obj = getattr(p, "tier")
        tier = tier_obj.value if hasattr(tier_obj, "value") else str(tier_obj)
        out[name] = tier
    return out


def display_tier_editor():
    st.header("🧩 Tier Editor (Postgres)")
    st.caption("Edit Scorito tiers (A/B/C/D) and save to Postgres. Create a new tier set per Grand Slam.")

    gender = st.radio("Gender", options=["men", "women"], horizontal=True)

    # Optional DB URL override for the dashboard process
    with st.sidebar.expander("DB connection (optional)"):
        st.write("By default this tries `TENNIS_DB_URL`, then `DATABASE_URL`, then derives from `infra/tennis_dagster/tennis_dagster.env`.")
        st.text_input("TENNIS_DB_URL (restart app after change)", value=os.getenv("TENNIS_DB_URL", ""), key="tennis_db_url_hint")

    engine = get_engine()
    ensure_tier_tables(engine)

    active_id = get_active_tier_set_id(engine, gender)
    tier_sets = list_tier_sets(engine, gender)

    colA, colB, colC = st.columns([2, 2, 2])
    with colA:
        st.subheader("Tier set")
        if tier_sets:
            options = {f"#{t['id']} — {t['name']} ({t['created_at']}){' [ACTIVE]' if t['active'] else ''}": t["id"] for t in tier_sets}
            selected_label = st.selectbox("Select tier set", options=list(options.keys()))
            selected_id = options[selected_label]
        else:
            st.warning("No tier sets yet.")
            selected_id = None

    with colB:
        st.subheader("Create / copy")
        new_name = st.text_input("New tier set name", value=f"{gender}_tiers")
        tournament = st.text_input("Tournament (optional, e.g. AO/RG/WIM/USO)", value="")
        year = st.number_input("Year (optional)", min_value=1900, max_value=2100, value=2026)
        make_active = st.checkbox("Make active", value=True)

        if st.button("Create empty tier set"):
            new_id = create_tier_set(
                engine,
                name=new_name,
                gender=gender,
                tournament=tournament or None,
                year=int(year) if year else None,
                make_active=make_active,
            )
            st.success(f"Created tier set {new_id}")
            st.rerun()

        if selected_id and st.button("Copy selected tier set"):
            new_id = copy_tier_set(
                engine,
                from_tier_set_id=int(selected_id),
                name=new_name,
                gender=gender,
                tournament=tournament or None,
                year=int(year) if year else None,
                make_active=make_active,
            )
            st.success(f"Copied to new tier set {new_id}")
            st.rerun()

    with colC:
        st.subheader("Import")
        st.write("Seed from the current `data/import/*_database.py` tiers.")
        if st.button("Import from python files into new tier set"):
            tiers_map = _extract_tiers_from_import_files(gender)
            new_id = create_tier_set(
                engine,
                name=f"initial_from_import_files_{gender}",
                gender=gender,
                tournament=None,
                year=None,
                make_active=True,
            )
            upsert_tiers(engine, tier_set_id=new_id, gender=gender, tiers=tiers_map)
            st.success(f"Imported {len(tiers_map)} players into tier set {new_id} and set active")
            st.rerun()

        if active_id and st.button("Set selected as active") and selected_id:
            set_active_tier_set(engine, gender, int(selected_id))
            st.success(f"Set tier set {selected_id} active for {gender}")
            st.rerun()

    if not selected_id:
        return

    # Ensure all Elo-ranked players are present in this tier set (default tier D)
    try:
        added = ensure_tier_set_has_all_elo_current_players(
            engine, tier_set_id=int(selected_id), gender=gender, default_tier="D"
        )
        if added > 0:
            st.info(f"Added {added} missing Elo-ranked players to this tier set as Tier D.")
    except Exception as e:
        st.warning(f"Could not auto-add missing Elo-ranked players: {e}")

    st.subheader("Edit tiers")
    rows = load_tiers(engine, int(selected_id))
    if not rows:
        st.info("No tiers in this set yet. Import or add players via sync script.")
        return

    df = pd.DataFrame(rows)
    search = st.text_input("Filter player name", value="")
    if search:
        df = df[df["player_name"].str.contains(search, case=False, na=False)]

    edited = st.data_editor(
        df,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "tier": st.column_config.SelectboxColumn("Tier", options=TIERS, required=True),
        },
        disabled=["player_name"],
        key=f"tier_editor_{gender}_{selected_id}",
    )

    if st.button("💾 Save tiers to Postgres", type="primary"):
        mapping = {row["player_name"]: row["tier"] for _, row in edited.iterrows()}
        upsert_tiers(engine, tier_set_id=int(selected_id), gender=gender, tiers=mapping)
        st.success(f"Saved {len(mapping)} tier assignments to tier set {selected_id}")


def main():
    """Main dashboard function"""
    st.markdown('<h1 class="main-header">🎾 Tennis Simulator Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🎾 Navigation")
    
    # Navigation
    page = st.sidebar.selectbox(
        "Select Page:",
        options=[
            'Database Overview', 'Player Search', 'Match Simulation', 'Elo Weights',
            'Single Tournament', 'Explorer', 'Scorito Game Analysis', 'Tier Editor'
        ],
        index=0
    )
    
    # Page routing
    if page == 'Database Overview':
        # Gender selection only for Database Overview
        gender = st.sidebar.selectbox(
            "Select Gender:",
            options=['men', 'women'],
            format_func=lambda x: x.title()
        )
        
        df = load_database_df(gender)
        if df.empty:
            st.error("Failed to load database.")
            return
        df = display_database_overview_from_df(df, gender)
        
        # Show top players
        st.subheader("🏆 Top Players by Elo")
        if "elo" in df.columns and not df['elo'].isna().all():
            top_players = df.nlargest(10, 'elo')[['name', 'tier', 'elo', 'ranking']]
            st.dataframe(top_players, use_container_width=True)
        
        # Footer info for Database Overview
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Database Info:**")
        st.sidebar.markdown(f"• Gender: {gender.title()}")
        st.sidebar.markdown(f"• Players: {len(df)}")
        
        # Show database stats in sidebar
        if not df.empty:
            tier_counts = pd.Series(df["tier"]).value_counts().sort_index()
            
            st.sidebar.markdown("**Tier Distribution:**")
            for tier, count in tier_counts.items():
                st.sidebar.markdown(f"• Tier {tier}: {count}")
    
    elif page == 'Player Search':
        # Gender selection for Player Search
        gender = st.sidebar.selectbox(
            "Select Gender:",
            options=['men', 'women'],
            format_func=lambda x: x.title(),
            key="player_search_gender"
        )
        
        df = load_database_df(gender)
        if df.empty:
            st.error("Failed to load database.")
            return
        # Adapt to search component expectations, and include form + rank columns.
        df2 = df.rename(
            columns={
                "name": "Name",
                "tier": "Tier",
                "elo": "Elo",
                "helo": "hElo",
                "celo": "cElo",
                "gelo": "gElo",
                "ranking": "Ranking",
                "form": "Form",
                "elo_rank": "Elo Rank",
                "as_of": "As Of",
            }
        )

        # Compute ranks for rating columns (1 = best). Missing values remain NaN.
        for col, out_col in [
            ("Elo", "Elo Value Rank"),
            ("hElo", "hElo Value Rank"),
            ("cElo", "cElo Value Rank"),
            ("gElo", "gElo Value Rank"),
            ("Form", "Form Rank"),
        ]:
            if col in df2.columns:
                df2[out_col] = df2[col].rank(ascending=False, method="min")
        display_player_search(df2)
    
    elif page == 'Match Simulation':
        # Gender selection for Match Simulation
        gender = st.sidebar.selectbox(
            "Select Gender:",
            options=['men', 'women'],
            format_func=lambda x: x.title(),
            key="match_sim_gender"
        )
        
        df = load_database_df(gender)
        if df.empty:
            st.error("Failed to load database.")
            return
        display_match_simulation_from_df(df, gender)
    
    elif page == 'Elo Weights':
        display_elo_weights_config()
    
    elif page == 'Single Tournament':
        display_single_tournament()
    
    elif page == 'Explorer':
        display_explorer()
    
    elif page == 'Scorito Game Analysis':
        display_scorito_game_analysis()
    
    elif page == 'Tier Editor':
        display_tier_editor()


if __name__ == "__main__":
    main() 