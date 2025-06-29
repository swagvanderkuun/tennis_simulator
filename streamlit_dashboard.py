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
import plotly.graph_objects as go

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
    player = Player(
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
            'yElo': data.yelo,
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
            st.markdown(f"Form: {player1.form:.1f}" if hasattr(player1, 'form') and player1.form is not None else "Form: N/A")
        
        with col2:
            st.markdown(f"**{player2.name}**")
            st.markdown(f"Tier: {player2.tier.value}")
            st.markdown(f"Elo: {player2.elo:.1f}")
            st.markdown(f"hElo: {player2.helo:.1f}")
            st.markdown(f"cElo: {player2.celo:.1f}")
            st.markdown(f"gElo: {player2.gelo:.1f}")
            st.markdown(f"yElo: {player2.yelo:.1f}")
            st.markdown(f"Form: {player2.form:.1f}" if hasattr(player2, 'form') and player2.form is not None else "Form: N/A")
        
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
    """Display Elo weights configuration interface."""
    st.header('⚖️ Elo Weights Configuration')
    st.write('Configure the weights for different Elo rating types in match simulation.')
    
    # Get current weights from session state or use defaults
    if 'preset_elo' in st.session_state:
        # Use preset values if available
        elo_default = st.session_state.preset_elo
        helo_default = st.session_state.preset_helo
        celo_default = st.session_state.preset_celo
        gelo_default = st.session_state.preset_gelo
        yelo_default = st.session_state.preset_yelo
        # Clear preset values after using them
        del st.session_state.preset_elo
        del st.session_state.preset_helo
        del st.session_state.preset_celo
        del st.session_state.preset_gelo
        del st.session_state.preset_yelo
    elif 'global_weights' in st.session_state:
        current_weights = st.session_state.global_weights
        elo_default = current_weights.elo_weight
        helo_default = current_weights.helo_weight
        celo_default = current_weights.celo_weight
        gelo_default = current_weights.gelo_weight
        yelo_default = current_weights.yelo_weight
    else:
        elo_default = 0.4
        helo_default = 0.2
        celo_default = 0.2
        gelo_default = 0.1
        yelo_default = 0.1
    
    # Weight configuration
    st.subheader('Weight Configuration')
    st.write('Adjust the weights for each Elo type. Weights must sum to 1.0.')
    
    col1, col2 = st.columns(2)
    
    with col1:
        elo_weight = st.slider('Overall Elo Weight', 0.0, 1.0, elo_default, 0.05, key="elo_weight")
        helo_weight = st.slider('Hard Court Elo Weight', 0.0, 1.0, helo_default, 0.05, key="helo_weight")
        celo_weight = st.slider('Clay Court Elo Weight', 0.0, 1.0, celo_default, 0.05, key="celo_weight")
    
    with col2:
        gelo_weight = st.slider('Grass Court Elo Weight', 0.0, 1.0, gelo_default, 0.05, key="gelo_weight")
        yelo_weight = st.slider('Year-to-Date Elo Weight', 0.0, 1.0, yelo_default, 0.05, key="yelo_weight")
    
    # Calculate total weight
    total_weight = elo_weight + helo_weight + celo_weight + gelo_weight + yelo_weight
    
    # Display total weight
    if abs(total_weight - 1.0) < 0.01:
        st.success(f'✅ Total Weight: {total_weight:.2f}')
    else:
        st.error(f'❌ Total Weight: {total_weight:.2f} (must be 1.0)')
    
    # Preset configurations
    st.subheader('Preset Configurations')
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button('Hard Court Focus'):
            # Store preset values in different session state keys
            st.session_state.preset_elo = 0.3
            st.session_state.preset_helo = 0.4
            st.session_state.preset_celo = 0.1
            st.session_state.preset_gelo = 0.1
            st.session_state.preset_yelo = 0.1
            st.rerun()
    
    with col2:
        if st.button('Clay Court Focus'):
            st.session_state.preset_elo = 0.3
            st.session_state.preset_helo = 0.1
            st.session_state.preset_celo = 0.4
            st.session_state.preset_gelo = 0.1
            st.session_state.preset_yelo = 0.1
            st.rerun()
    
    with col3:
        if st.button('Grass Court Focus'):
            st.session_state.preset_elo = 0.3
            st.session_state.preset_helo = 0.1
            st.session_state.preset_celo = 0.1
            st.session_state.preset_gelo = 0.4
            st.session_state.preset_yelo = 0.1
            st.rerun()
    
    # Apply weights button
    if st.button('Apply Weights', type='primary'):
        if abs(total_weight - 1.0) < 0.01:
            weights = EloWeights(
                elo_weight=elo_weight,
                helo_weight=helo_weight,
                celo_weight=celo_weight,
                gelo_weight=gelo_weight,
                yelo_weight=yelo_weight
            )
            st.session_state.global_weights = weights
            st.success('✅ Weights applied successfully! These weights will be used in all simulators.')
            return weights
        else:
            st.error('❌ Weights must sum to 1.0. Please adjust the weights.')
            return None
    
    # Show current weights if available
    if 'global_weights' in st.session_state:
        st.subheader('Current Global Weights')
        weights = st.session_state.global_weights
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Overall Elo", f"{weights.elo_weight:.2f}")
            st.metric("Hard Elo", f"{weights.helo_weight:.2f}")
            st.metric("Clay Elo", f"{weights.celo_weight:.2f}")
        with col2:
            st.metric("Grass Elo", f"{weights.gelo_weight:.2f}")
            st.metric("Year-to-date Elo", f"{weights.yelo_weight:.2f}")
    
    return None


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
                try:
                    sim.set_custom_weights(st.session_state.global_weights)
                    st.info("Using global Elo weights.")
                except AttributeError as e:
                    st.error(f"Error setting custom weights: {e}")
                    st.warning("Continuing with default weights.")
                except Exception as e:
                    st.error(f"Unexpected error setting weights: {e}")
                    st.warning("Continuing with default weights.")
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
    db = populate_static_database(gender)
    players = [p for p in db.values()]
    match_simulator = create_match_simulator()
    
    # Add global weights option
    if 'global_weights' in st.session_state:
        st.info("Global Elo weights are available and will be used.")
    
    if st.button('Run Single Tournament Simulation'):
        # Setup and simulate tournament
        sim = FixedDrawEloSimulator()
        
        # Apply global weights if available
        if 'global_weights' in st.session_state:
            try:
                sim.set_custom_weights(st.session_state.global_weights)
            except Exception as e:
                st.warning(f"Could not apply global weights: {e}. Using default weights.")
        
        sim.setup_tournaments()
        tournament = sim.men_tournament if gender == 'men' else sim.women_tournament
        sim.simulate_tournament(tournament)
        winner = tournament.winner.name if tournament.winner else '?'
        st.success(f'Winner: {winner}')
        # Build bracket tree from matches
        bracket_tree = sim.get_bracket_tree(tournament)
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
            st.metric("Year-to-date Elo", f"{weights.yelo_weight:.2f}")


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
    scoring, round_labels = parse_scorito_scoring()
    db = populate_static_database(gender)

    if st.button('Run Scorito Analysis'):
        with st.spinner(f'Running {num_simulations} simulations for Scorito analysis...'):
            sim = FixedDrawEloSimulator()
            sim.setup_tournaments()
            tournament = sim.men_tournament if gender == 'men' else sim.women_tournament

            player_points = {p.name: [] for p in tournament.players}

            for sim_idx in range(num_simulations):
                tournament.reset()
                sim.simulate_tournament(tournament)
                for p in tournament.players:
                    tier = get_player_tier(p)
                    # Fix: Map Round.W to the same index as Round.F (both are the final round)
                    round_to_index = {'R1': 0, 'R2': 1, 'R3': 2, 'R4': 3, 'QF': 4, 'SF': 5, 'F': 6, 'W': 6}
                    round_index = round_to_index.get(p.current_round.value, 0)
                    tier_scoring = scoring.get(tier, [0]*7)  # Back to 7 rounds
                    # Fix: Use cumulative points for all rounds reached (including winner)
                    total_points = sum(tier_scoring[:round_index + 1]) if round_index >= 0 else 0
                    player_points[p.name].append(total_points)

            avg_points = {name: sum(pts)/len(pts) if pts else 0 for name, pts in player_points.items()}

            for tier in ['A', 'B', 'C', 'D']:
                st.subheader(f'Top 6 Players - Tier {tier}')
                tier_players = []
                for name, data in db.items():
                    if data.tier.upper() == tier:
                        tier_players.append((name, avg_points.get(name, 0)))
                if tier_players:
                    tier_players.sort(key=lambda x: x[1], reverse=True)
                    top_6 = tier_players[:6]
                    data = [{'Player': name, 'Avg Points': f"{points:.2f}"} for name, points in top_6]
                    df = pd.DataFrame(data)
                    st.table(df)
                else:
                    st.info(f'No players found in Tier {tier}')
    else:
        st.info('Click "Run Scorito Analysis" to simulate and analyze Scorito points.')


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
            'Single Tournament', 'Explorer', 'Scorito Game Analysis'
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
        
        # Load database
        db = load_static_database(gender)
        
        if not db:
            st.error("Failed to load database. Please check the data files.")
            return
        
        df = display_database_overview(db, gender)
        
        # Show top players
        st.subheader("🏆 Top Players by Elo")
        if not df['Elo'].isna().all():
            top_players = df.nlargest(10, 'Elo')[['Name', 'Tier', 'Elo', 'Ranking']]
            st.dataframe(top_players, use_container_width=True)
        
        # Footer info for Database Overview
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
    
    elif page == 'Player Search':
        # Gender selection for Player Search
        gender = st.sidebar.selectbox(
            "Select Gender:",
            options=['men', 'women'],
            format_func=lambda x: x.title(),
            key="player_search_gender"
        )
        
        db = load_static_database(gender)
        if not db:
            st.error("Failed to load database. Please check the data files.")
            return
        
        df = pd.DataFrame([
            {
                'Name': name,
                'Tier': data.tier,
                'Elo': data.elo,
                'hElo': data.helo,
                'cElo': data.celo,
                'gElo': data.gelo,
                'yElo': data.yelo,
                'Form': data.form if hasattr(data, 'form') else None,
                'Ranking': data.ranking if hasattr(data, 'ranking') else None
            }
            for name, data in db.items()
        ])
        display_player_search(df)
    
    elif page == 'Match Simulation':
        # Gender selection for Match Simulation
        gender = st.sidebar.selectbox(
            "Select Gender:",
            options=['men', 'women'],
            format_func=lambda x: x.title(),
            key="match_sim_gender"
        )
        
        db = load_static_database(gender)
        if not db:
            st.error("Failed to load database. Please check the data files.")
            return
        display_match_simulation(db)
    
    elif page == 'Elo Weights':
        global_weights = display_elo_weights_config()
        if global_weights:
            st.session_state.global_weights = global_weights
    
    elif page == 'Single Tournament':
        display_single_tournament()
    
    elif page == 'Explorer':
        display_explorer()
    
    elif page == 'Scorito Game Analysis':
        display_scorito_game_analysis()


if __name__ == "__main__":
    main() 