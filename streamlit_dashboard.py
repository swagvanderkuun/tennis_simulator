#!/usr/bin/env python3
"""
Streamlit Dashboard for Tennis Simulator
Fast version using static database
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from typing import Dict, List, Optional
import random

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tennis_simulator.core.models import Player, Tier
from tennis_simulator.simulators.elo_match_simulator import EloMatchSimulator, EloWeights, create_match_simulator
from tennis_simulator.data.static_database import populate_static_database
from tennis_simulator.simulators.fixed_draw_elo_simulator import FixedDrawEloSimulator


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


@st.cache_data
def load_static_database(gender: str) -> Dict[str, any]:
    """Load static database with caching for performance"""
    try:
        db = populate_static_database(gender)
        return db
    except Exception as e:
        st.error(f"Error loading {gender} database: {e}")
        return {}


def create_player_from_static_data(name: str, data: any) -> Player:
    """Create Player object from static database data"""
    return Player(
        name=name,
        country="N/A",  # Static DB doesn't have country
        seeding=None,
        tier=Tier(data.tier),
        elo=data.elo,
        helo=data.helo,
        celo=data.celo,
        gelo=data.gelo,
        yelo=data.yelo,
        atp_rank=data.ranking if hasattr(data, 'ranking') else None,
        wta_rank=data.ranking if hasattr(data, 'ranking') else None
    )


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
            'yElo': data.yelo,
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
        st.dataframe(tier_filtered_df, use_container_width=True)


def display_match_simulation(db: Dict[str, any]):
    """Display match simulation interface"""
    st.subheader("🎾 Match Simulation")
    
    # Check if global weights are available
    if 'global_weights' in st.session_state:
        st.info("Using global Elo weights from the 'Elo Weights' tab.")
        simulator = EloMatchSimulator(weights=st.session_state.global_weights)
    else:
        st.warning("No global weights set. Using default weights. Set weights in the 'Elo Weights' tab.")
        simulator = create_match_simulator()
    
    # Player selection
    player_names = list(db.keys())
    
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
            st.markdown(f"yElo: {player1.yelo:.1f}")
        
        with col2:
            st.markdown(f"**{player2.name}**")
            st.markdown(f"Tier: {player2.tier.value}")
            st.markdown(f"Elo: {player2.elo:.1f}")
            st.markdown(f"hElo: {player2.helo:.1f}")
            st.markdown(f"cElo: {player2.celo:.1f}")
            st.markdown(f"gElo: {player2.gelo:.1f}")
            st.markdown(f"yElo: {player2.yelo:.1f}")
        
        # Calculate win probability
        win_prob = simulator.calculate_win_probability(player1, player2)
        
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
            winner, loser, details = simulator.simulate_match(player1, player2)
            
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
                    winner, _, _ = simulator.simulate_match(player1, player2)
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


def display_elo_weights_config():
    """Display Elo weights configuration that can be reused across all simulators"""
    st.subheader("⚖️ Elo Weights Configuration")
    st.markdown("Configure custom weights for Elo ratings. These weights will be used across all simulators.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        elo_weight = st.slider("Overall Elo Weight", 0.0, 1.0, 0.4, 0.05, key="global_elo")
        helo_weight = st.slider("Hard Elo Weight", 0.0, 1.0, 0.2, 0.05, key="global_helo")
        celo_weight = st.slider("Clay Elo Weight", 0.0, 1.0, 0.2, 0.05, key="global_celo")
    
    with col2:
        gelo_weight = st.slider("Grass Elo Weight", 0.0, 1.0, 0.1, 0.05, key="global_gelo")
        yelo_weight = st.slider("Year-to-date Elo Weight", 0.0, 1.0, 0.1, 0.05, key="global_yelo")
    
    total_weight = elo_weight + helo_weight + celo_weight + gelo_weight + yelo_weight
    
    if abs(total_weight - 1.0) > 0.001:
        st.error(f"⚠️ Weights must sum to 1.0. Current sum: {total_weight:.2f}")
        return None
    else:
        st.success(f"✅ Weights sum to {total_weight:.2f}")
        
        weights = EloWeights(
            elo_weight=elo_weight,
            helo_weight=helo_weight,
            celo_weight=celo_weight,
            gelo_weight=gelo_weight,
            yelo_weight=yelo_weight
        )
        
        return weights


def display_explorer():
    """Display the tournament explorer (multiple simulations)"""
    st.subheader("🔍 Tournament Explorer")
    st.markdown("Run multiple tournament simulations to explore win probabilities and outcomes.")

    gender = st.selectbox("Select Gender:", options=["men", "women"], format_func=lambda x: x.title(), key="explorer_gender")

    num_simulations = st.slider("Number of tournament simulations:", 10, 1000, 100, 10, key="explorer_sims")
    
    if st.button("Run Tournament Explorer", type="primary", key="explorer_btn"):
        with st.spinner("Running tournament explorer..."):
            sim = FixedDrawEloSimulator()
            
            # Use global weights if available
            if 'global_weights' in st.session_state:
                sim.set_custom_weights(st.session_state.global_weights)
                st.info("Using global Elo weights.")
            else:
                st.warning("No global weights set. Using default weights.")
            
            sim.setup_tournaments()
            if gender == "men":
                tournament = sim.men_tournament
            else:
                tournament = sim.women_tournament
            stats = sim.run_multiple_simulations(num_simulations)
            sim.print_simulation_summary(stats)
            
            # Display results in Streamlit
            st.success(f"Explored {num_simulations} tournaments for {gender.title()}.")
            st.subheader("Win Probabilities (Top 10)")
            win_probs = stats["men_win_probabilities"] if gender == "men" else stats["women_win_probabilities"]
            st.table(pd.DataFrame(list(win_probs.items()), columns=["Player", "Win Probability"]))
            st.subheader("Final Probabilities (Top 10)")
            final_probs = stats["men_final_probabilities"] if gender == "men" else stats["women_final_probabilities"]
            st.table(pd.DataFrame(list(final_probs.items()), columns=["Player", "Final Probability"]))
            st.subheader("Semifinal Probabilities (Top 10)")
            semi_probs = stats["men_semifinal_probabilities"] if gender == "men" else stats["women_semifinal_probabilities"]
            st.table(pd.DataFrame(list(semi_probs.items()), columns=["Player", "Semifinal Probability"]))


def display_single_tournament_simulation():
    """Display single tournament simulation"""
    st.subheader("🏆 Single Tournament Simulation")
    st.markdown("Simulate a single tournament and see the complete bracket with results.")

    gender = st.selectbox("Select Gender:", options=["men", "women"], format_func=lambda x: x.title(), key="single_gender")
    
    if st.button("Simulate Single Tournament", type="primary", key="single_btn"):
        with st.spinner("Simulating tournament..."):
            sim = FixedDrawEloSimulator()
            
            # Use global weights if available
            if 'global_weights' in st.session_state:
                sim.set_custom_weights(st.session_state.global_weights)
                st.info("Using global Elo weights.")
            else:
                st.warning("No global weights set. Using default weights.")
            
            sim.setup_tournaments()
            
            if gender == "men":
                tournament = sim.men_tournament
                winner = sim.simulate_tournament(tournament)
                st.success(f"🏆 **Men's Tournament Winner: {winner.name}**")
            else:
                tournament = sim.women_tournament
                winner = sim.simulate_tournament(tournament)
                st.success(f"🏆 **Women's Tournament Winner: {winner.name}**")
            
            # Display tournament bracket
            st.subheader("Tournament Bracket")
            
            # Get all matches from the tournament
            if tournament.matches:
                # Group matches by round
                matches_by_round = {}
                for match in tournament.matches:
                    round_name = match.round.name
                    if round_name not in matches_by_round:
                        matches_by_round[round_name] = []
                    matches_by_round[round_name].append(match)
                
                # Display matches by round
                for round_name in ['R64', 'R32', 'R16', 'QF', 'SF', 'F']:
                    if round_name in matches_by_round:
                        st.markdown(f"**{round_name}:**")
                        for match in matches_by_round[round_name]:
                            winner_name = match.winner.name if match.winner else "TBD"
                            loser_name = match.loser.name if match.loser else "TBD"
                            st.write(f"  {winner_name} def. {loser_name}")
                        st.write("")


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
            st.metric("Year-to-date Elo", f"{weights.yelo_weight:.2f}")


def main():
    """Main dashboard function"""
    st.markdown('<h1 class="main-header">🎾 Tennis Simulator Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🎾 Navigation")
    
    # Gender selection
    gender = st.sidebar.selectbox(
        "Select Gender:",
        options=['men', 'women'],
        format_func=lambda x: x.title()
    )
    
    # Load database
    db = load_static_database(gender)
    
    if not db:
        st.error("Failed to load database. Please check the data files.")
        return
    
    # Navigation
    page = st.sidebar.selectbox(
        "Select Page:",
        options=['Database Overview', 'Player Search', 'Match Simulation', 'Elo Weights', 'Single Tournament', 'Explorer'],
        index=0
    )
    
    # Page routing
    if page == 'Database Overview':
        df = display_database_overview(db, gender)
        
        # Show top players
        st.subheader("🏆 Top Players by Elo")
        if not df['Elo'].isna().all():
            top_players = df.nlargest(10, 'Elo')[['Name', 'Tier', 'Elo', 'Ranking']]
            st.dataframe(top_players, use_container_width=True)
    
    elif page == 'Player Search':
        df = pd.DataFrame([
            {
                'Name': name,
                'Tier': data.tier,
                'Elo': data.elo,
                'hElo': data.helo,
                'cElo': data.celo,
                'gElo': data.gelo,
                'yElo': data.yelo,
                'Ranking': data.ranking if hasattr(data, 'ranking') else None
            }
            for name, data in db.items()
        ])
        display_player_search(df)
    
    elif page == 'Match Simulation':
        display_match_simulation(db)
    
    elif page == 'Elo Weights':
        global_weights = display_elo_weights_config()
        if global_weights:
            st.session_state.global_weights = global_weights
    
    elif page == 'Single Tournament':
        display_single_tournament_simulation()
    
    elif page == 'Explorer':
        display_explorer()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Database Info:**")
    st.sidebar.markdown(f"• Gender: {gender.title()}")
    st.sidebar.markdown(f"• Players: {len(db)}")
    
    # Show database stats in sidebar
    if db:
        tiers = [data.tier for data in db.values()]
        tier_counts = pd.Series(tiers).value_counts().sort_index()
        
        st.sidebar.markdown("**Tier Distribution:**")
        for tier, count in tier_counts.items():
            st.sidebar.markdown(f"• Tier {tier}: {count}")


if __name__ == "__main__":
    main() 