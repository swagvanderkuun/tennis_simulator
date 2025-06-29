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
import plotly.express as px

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tennis_simulator.core.models import Player, Tier
from tennis_simulator.simulators.elo_match_simulator import EloMatchSimulator, EloWeights, create_match_simulator
from tennis_simulator.data.static_database import populate_static_database
from tennis_simulator.simulators.fixed_draw_elo_simulator import FixedDrawEloSimulator

# Add custom CSS for better dark mode support
st.markdown("""
<style>
/* Dark mode compatible styling */
.stats-container {
    display: flex;
    justify-content: space-around;
    margin: 20px 0;
    flex-wrap: wrap;
}

.stat-item {
    text-align: center;
    padding: 15px;
    margin: 10px;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    min-width: 120px;
}

.stat-number {
    font-size: 2em;
    font-weight: bold;
    color: #00ff88;
    margin-bottom: 5px;
}

.stat-label {
    font-size: 0.9em;
    color: inherit;
    opacity: 0.8;
}

.feature-card {
    background: rgba(255, 255, 255, 0.15);
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.feature-card h3 {
    color: #00ff88;
    margin-bottom: 15px;
    font-weight: bold;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.feature-card ul {
    margin: 0;
    padding-left: 20px;
}

.feature-card li {
    margin: 8px 0;
    color: rgba(255, 255, 255, 0.95);
    font-weight: 500;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.highlight-box {
    background: rgba(255, 255, 255, 0.12);
    border: 2px solid rgba(255, 255, 255, 0.25);
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.2);
}

.highlight-box h4 {
    color: #00ff88;
    margin-bottom: 10px;
    font-weight: bold;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.highlight-box ul {
    margin: 0;
    padding-left: 15px;
}

.highlight-box li {
    margin: 5px 0;
    color: rgba(255, 255, 255, 0.9);
    font-weight: 500;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* Ensure text is visible in both light and dark modes */
.stMarkdown, .stText {
    color: inherit !important;
}

/* Make sure links are visible */
a {
    color: #00ff88 !important;
}

/* Ensure tables are readable */
.dataframe {
    background-color: transparent !important;
}

/* Plotly chart improvements for dark mode */
.js-plotly-plot .plotly .main-svg {
    background-color: transparent !important;
}

/* Additional dark mode improvements */
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
    color: rgba(255, 255, 255, 0.95) !important;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.stMarkdown p {
    color: rgba(255, 255, 255, 0.85) !important;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

/* Strong emphasis for important text */
strong {
    color: rgba(255, 255, 255, 0.98) !important;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

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
        print(f"Loading {gender} database...")
        db = populate_static_database(gender)
        
        if not db:
            st.warning(f"No {gender} players found in database. This might be due to data loading issues in the hosted environment.")
            return {}
        
        print(f"Successfully loaded {len(db)} {gender} players")
        return db
        
    except FileNotFoundError as e:
        st.error(f"Data files not found for {gender} database: {e}")
        st.info("The application is trying to load data files. In hosted environments, this might fail if files are not accessible.")
        return {}
        
    except ImportError as e:
        st.error(f"Import error loading {gender} database: {e}")
        st.info("This might be due to missing dependencies or module path issues.")
        return {}
        
    except Exception as e:
        st.error(f"Unexpected error loading {gender} database: {e}")
        st.info("Please check the console logs for more details.")
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


def display_overview():
    """Display the overview/homepage of the tennis simulator dashboard"""
    st.markdown("""
    # 🎾 Tennis Simulator Dashboard
    
    Welcome to the ultimate tennis tournament simulation platform! This dashboard provides comprehensive tools for analyzing ATP and WTA Grand Slam tournaments with advanced Elo-based match prediction and form analysis.
    """)
    
    # Getting Started section - moved up for better UX
    st.markdown("---")
    st.markdown("## 🚀 Getting Started")
    st.write("Ready to dive into the world of tennis simulation? Here's how to get started:")
    
    # Getting started steps in a nice grid
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🎯 Quick Start:**
        1. **Match Simulation** - Compare any two players
        2. **Single Tournament** - Run a complete tournament
        3. **Tournament Explorer** - Analyze with 1000+ simulations
        """)
    
    with col2:
        st.markdown("""
        **⚙️ Advanced Features:**
        4. **Elo Weights** - Fine-tune simulation parameters
        5. **Player Database** - Explore comprehensive player data
        6. **Scorito Analysis** - Optimize fantasy tennis strategy
        """)
    
    st.success("🎾 **Ready to simulate!** Choose any feature from the sidebar to begin your tennis analysis journey.")
    
    # Statistics section with better visual appeal
    st.markdown("---")
    st.markdown("## 📊 Dashboard Statistics")
    
    # Use metrics with better styling
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Men's Players", 
            value="487",
            help="Complete ATP roster with ratings and form data"
        )
    with col2:
        st.metric(
            label="Women's Players", 
            value="515",
            help="Full WTA database with comprehensive statistics"
        )
    with col3:
        st.metric(
            label="Elo Rating Types", 
            value="5",
            help="Overall, Hard, Clay, Grass, and Year-to-date ratings"
        )
    with col4:
        st.metric(
            label="Preset Configurations", 
            value="4",
            help="Optimized weight combinations for different scenarios"
        )
    
    # Key Features section with better visual hierarchy
    st.markdown("---")
    st.markdown("## ⭐ Key Features")
    st.write("Our simulator combines cutting-edge statistical analysis with real tournament data to deliver the most accurate tennis predictions available.")
    
    # Feature grid with better spacing
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.markdown("### 🏆 Tournament Simulation")
            st.markdown("""
            - **Fixed Draw Structure:** Uses real tournament draws from import data
            - **Best-of-5 for Men:** Advanced probability adjustment for men's matches
            - **Best-of-3 for Women:** Standard calculation for women's matches
            - **Bracket Visualization:** Interactive tournament brackets with Plotly
            """)
            
            st.markdown("### 📊 Advanced Analytics")
            st.markdown("""
            - **Multi-Format Elo:** Overall, Hard, Clay, Grass, and Year-to-date ratings
            - **Form Analysis:** Recent performance metrics with configurable weights
            - **Win Probability:** Blended Elo and form-based predictions
            - **Statistical Insights:** Comprehensive simulation statistics
            """)
    
    with col2:
        with st.container():
            st.markdown("### 🎯 Match Simulation")
            st.markdown("""
            - **Head-to-Head Analysis:** Detailed player comparisons
            - **Real-time Predictions:** Instant win probability calculations
            - **Multiple Simulations:** Monte Carlo analysis with customizable runs
            - **Form Integration:** Recent performance impact on predictions
            """)
            
            st.markdown("### 🎮 Scorito Game Analysis")
            st.markdown("""
            - **Tier-Based Scoring:** A, B, C, D player tier system
            - **Point Optimization:** Find the best players per tier
            - **Round-by-Round Analysis:** Cumulative scoring simulation
            - **Strategic Insights:** Maximize your fantasy tennis points
            """)
    
    # Database section with better organization
    st.markdown("---")
    st.markdown("## 📋 Player Database")
    st.write("Access comprehensive player data for both ATP and WTA tours:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 👥 Player Profiles")
        st.markdown("""
        - **487 Men's Players:** Complete ATP roster
        - **515 Women's Players:** Full WTA database
        - **Tier Classification:** A, B, C, D performance tiers
        - **Current Rankings:** ATP/WTA rankings included
        """)
    
    with col2:
        st.markdown("### 📈 Rating Systems")
        st.markdown("""
        - **Overall Elo:** General performance rating
        - **Surface-Specific:** Hard, Clay, Grass court ratings
        - **Year-to-Date:** Current season performance
        - **Form Metrics:** Recent match performance data
        """)
    
    with col3:
        st.markdown("### 🔍 Search & Filter")
        st.markdown("""
        - **Name Search:** Quick player lookup
        - **Tier Filtering:** Find players by performance tier
        - **Rating Analysis:** Compare player statistics
        - **Export Options:** Download player data
        """)
    
    # Simulation capabilities with better visual appeal
    st.markdown("---")
    st.markdown("## 🎲 Simulation Capabilities")
    st.write("Experience the most advanced tennis simulation technology:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏅 Single Tournament")
        st.markdown("""
        - **Real Draw Structure:** Based on actual tournament brackets
        - **Instant Results:** Complete tournament simulation
        - **Winner Prediction:** See who emerges victorious
        - **Bracket Visualization:** Beautiful interactive brackets
        """)
        
        st.markdown("### 🔬 Tournament Explorer")
        st.markdown("""
        - **1000+ Simulations:** Monte Carlo analysis
        - **Probability Mapping:** Win, final, semifinal probabilities
        - **Statistical Analysis:** Comprehensive result breakdown
        - **Trend Identification:** Discover patterns and favorites
        """)
    
    with col2:
        st.markdown("### ⚖️ Elo Weights Configuration")
        st.markdown("""
        - **Custom Weighting:** Adjust Elo component importance
        - **Form Integration:** Blend recent performance with ratings
        - **Surface Optimization:** Fine-tune for specific courts
        - **Real-time Updates:** Instant parameter adjustment
        """)
        
        st.markdown("### 🎯 Match Analysis")
        st.markdown("""
        - **Head-to-Head:** Detailed player comparisons
        - **Probability Breakdown:** Standard vs form-based predictions
        - **Multiple Runs:** Statistical validation
        - **Visual Results:** Charts and graphs for insights
        """)
    
    # Technical highlights with better organization
    st.markdown("---")
    st.markdown("## 🔧 Technical Highlights")
    st.write("Built with cutting-edge technology for maximum accuracy and performance:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🧮 Advanced Algorithms")
        st.markdown("""
        - **Elo Rating System:** Industry-standard tennis rating methodology
        - **Form Integration:** Recent performance weighting with configurable parameters
        - **Surface Specialization:** Optimized weights for different court types
        - **Probability Blending:** Sophisticated combination of multiple prediction models
        """)
        
        st.markdown("### 📊 Data Integration")
        st.markdown("""
        - **Real Tournament Data:** Actual draw structures from Grand Slam events
        - **Comprehensive Player Database:** 1000+ players with complete statistics
        - **Multiple Rating Types:** Overall, surface-specific, and year-to-date ratings
        - **Form Metrics:** Recent match performance analysis
        """)
    
    with col2:
        st.markdown("### 🎨 User Experience")
        st.markdown("""
        - **Interactive Visualizations:** Beautiful Plotly charts and graphs
        - **Real-time Updates:** Instant parameter adjustment and simulation
        - **Comprehensive Analysis:** Multiple simulation types and statistical insights
        - **User-friendly Interface:** Intuitive design for both casual and advanced users
        """)
        
        st.markdown("### 🚀 Performance")
        st.markdown("""
        - **Fast Simulation:** Optimized algorithms for quick results
        - **Scalable Architecture:** Handle thousands of simulations efficiently
        - **Memory Efficient:** Smart data management for large datasets
        - **Cross-platform:** Works on any device with a web browser
        """)


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


def display_match_simulation(db: Dict[str, any], gender: str = 'women'):
    """Display match simulation interface"""
    st.subheader("🎾 Match Simulation")
    
    # Check if global weights are available
    if 'global_weights' in st.session_state:
        st.info("Using global Elo weights from the 'Elo Weights' tab.")
        simulator = EloMatchSimulator(weights=st.session_state.global_weights)
        
        # Show current form parameters
        weights = st.session_state.global_weights
        st.info(f"Form parameters: k={weights.form_k:.3f}, α={weights.form_alpha:.2f}")
    else:
        st.warning("No global weights set. Using default weights. Set weights in the 'Elo Weights' tab.")
        simulator = create_match_simulator()
    
    # Show gender-specific information
    if gender == 'men':
        st.info("🏆 Men's matches use best-of-5 sets (five-set probability adjustment applied)")
    else:
        st.info("🏆 Women's matches use best-of-3 sets (standard probability calculation)")
    
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


def display_elo_weights_config():
    """Display Elo weights configuration interface."""
    st.header('⚖️ Elo Weights Configuration')
    st.write('Configure the weights for different Elo rating types in match simulation.')
    
    # Get current weights from session state or use defaults
    if 'preset_elo' in st.session_state and 'preset_used' not in st.session_state:
        # Use preset values if available and not yet used
        elo_default = st.session_state.preset_elo
        helo_default = st.session_state.preset_helo
        celo_default = st.session_state.preset_celo
        gelo_default = st.session_state.preset_gelo
        yelo_default = st.session_state.preset_yelo
        form_k_default = st.session_state.preset_form_k
        form_alpha_default = st.session_state.preset_form_alpha
        # Mark preset as used
        st.session_state.preset_used = True
    elif 'global_weights' in st.session_state:
        current_weights = st.session_state.global_weights
        elo_default = current_weights.elo_weight
        helo_default = current_weights.helo_weight
        celo_default = current_weights.celo_weight
        gelo_default = current_weights.gelo_weight
        yelo_default = current_weights.yelo_weight
        form_k_default = current_weights.form_k
        form_alpha_default = current_weights.form_alpha
    else:
        elo_default = 0.1
        helo_default = 0.1
        celo_default = 0.0
        gelo_default = 0.4
        yelo_default = 0.4
        form_k_default = 0.03
        form_alpha_default = 0.95
    
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
    
    # Form configuration
    st.subheader('Form Configuration')
    st.write('Configure form-based probability calculation.')
    
    col1, col2 = st.columns(2)
    
    with col1:
        form_k = st.slider('Form Steepness (k)', 0.01, 0.5, form_k_default, 0.01, 
                          help="Controls how steeply form differences affect probability. Higher values = more impact.",
                          key="form_k_slider")
    
    with col2:
        form_alpha = st.slider('Form Weight (α)', 0.0, 1.0, form_alpha_default, 0.05,
                              help="Weight for blending standard Elo (α) vs form probability (1-α). α=1.0 = Elo only, α=0.0 = Form only.",
                              key="form_alpha_slider")
    
    # Calculate total weight
    total_weight = elo_weight + helo_weight + celo_weight + gelo_weight + yelo_weight
    
    # Display total weight
    if abs(total_weight - 1.0) < 0.01:
        st.success(f'✅ Total Weight: {total_weight:.2f}')
        # Automatically save weights when they sum to 1.0
        weights = EloWeights(
            elo_weight=elo_weight,
            helo_weight=helo_weight,
            celo_weight=celo_weight,
            gelo_weight=gelo_weight,
            yelo_weight=yelo_weight,
            form_k=form_k,
            form_alpha=form_alpha
        )
        st.session_state.global_weights = weights
        st.success('✅ Weights automatically saved! These weights will be used in all simulators.')
        st.info('💡 Changes are saved automatically when weights sum to 1.0. No need to click any buttons!')
    else:
        st.error(f'❌ Total Weight: {total_weight:.2f} (must be 1.0)')
        st.warning('Weights will be saved automatically when they sum to 1.0.')
    
    # Preset configurations
    st.subheader('Preset Configurations')
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button('🎾 Default Preset'):
            # Clear any existing preset usage flag
            if 'preset_used' in st.session_state:
                del st.session_state.preset_used
            # Store preset values in different session state keys
            st.session_state.preset_elo = 0.1
            st.session_state.preset_helo = 0.1
            st.session_state.preset_celo = 0.0
            st.session_state.preset_gelo = 0.4
            st.session_state.preset_yelo = 0.4
            st.session_state.preset_form_k = 0.03
            st.session_state.preset_form_alpha = 0.95
            st.rerun()
    
    with col2:
        if st.button('🏟️ Hard Court Focus'):
            # Clear any existing preset usage flag
            if 'preset_used' in st.session_state:
                del st.session_state.preset_used
            # Store preset values in different session state keys
            st.session_state.preset_elo = 0.3
            st.session_state.preset_helo = 0.4
            st.session_state.preset_celo = 0.1
            st.session_state.preset_gelo = 0.1
            st.session_state.preset_yelo = 0.1
            st.session_state.preset_form_k = 0.03
            st.session_state.preset_form_alpha = 0.95
            st.rerun()
    
    with col3:
        if st.button('🏖️ Clay Court Focus'):
            # Clear any existing preset usage flag
            if 'preset_used' in st.session_state:
                del st.session_state.preset_used
            st.session_state.preset_elo = 0.3
            st.session_state.preset_helo = 0.1
            st.session_state.preset_celo = 0.4
            st.session_state.preset_gelo = 0.1
            st.session_state.preset_yelo = 0.1
            st.session_state.preset_form_k = 0.03
            st.session_state.preset_form_alpha = 0.95
            st.rerun()
    
    with col4:
        if st.button('🌱 Grass Court Focus'):
            # Clear any existing preset usage flag
            if 'preset_used' in st.session_state:
                del st.session_state.preset_used
            st.session_state.preset_elo = 0.3
            st.session_state.preset_helo = 0.1
            st.session_state.preset_celo = 0.1
            st.session_state.preset_gelo = 0.4
            st.session_state.preset_yelo = 0.1
            st.session_state.preset_form_k = 0.03
            st.session_state.preset_form_alpha = 0.95
            st.rerun()

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
            st.metric("Year-to-date Elo", f"{weights.yelo_weight:.2f}")
        with col3:
            st.metric("Form Steepness (k)", f"{weights.form_k:.3f}")
            st.metric("Form Weight (α)", f"{weights.form_alpha:.2f}")


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
                    weights = st.session_state.global_weights
                    st.info(f"Using global Elo weights. Form parameters: k={weights.form_k:.3f}, α={weights.form_alpha:.2f}")
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
        weights = st.session_state.global_weights
        st.info(f"Global Elo weights are available and will be used. Form parameters: k={weights.form_k:.3f}, α={weights.form_alpha:.2f}")
    
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
            fig.add_shape(type='line', x0=line['x0'], y0=line['y0'], x1=line['x1'], y1=line['y1'], line=dict(color='rgba(255, 255, 255, 0.3)', width=1))
        fig.add_trace(go.Scatter(x=xs, y=ys, mode='markers+text', text=labels, textposition='middle right', 
                                marker=dict(size=8, color='#00ff88'), 
                                textfont=dict(color='white', size=10),
                                hovertext=winners, hoverinfo='text'))
        fig.update_layout(
            height=1200, 
            width=1600, 
            showlegend=False, 
            margin=dict(l=20, r=20, t=40, b=20), 
            xaxis=dict(showticklabels=False), 
            yaxis=dict(showticklabels=False), 
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
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
    
    # Show current weights info
    if 'global_weights' in st.session_state:
        weights = st.session_state.global_weights
        st.info(f"Using global Elo weights. Form parameters: k={weights.form_k:.3f}, α={weights.form_alpha:.2f}")
    else:
        st.warning("No global weights set. Using default weights.")
    
    if 'bracket_simulator' not in st.session_state:
        st.session_state['bracket_simulator'] = FixedDrawEloSimulator()
        
        # Apply global weights if available
        if 'global_weights' in st.session_state:
            try:
                st.session_state['bracket_simulator'].set_custom_weights(st.session_state.global_weights)
            except Exception as e:
                st.warning(f"Could not apply global weights: {e}. Using default weights.")
        
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
            fig.add_shape(type='line', x0=line['x0'], y0=line['y0'], x1=line['x1'], y1=line['y1'], line=dict(color='rgba(255, 255, 255, 0.3)', width=1))
        # Draw nodes
        fig.add_trace(go.Scatter(x=xs, y=ys, mode='markers+text', text=labels, textposition='middle right', 
                                marker=dict(size=8, color='#00ff88'), 
                                textfont=dict(color='white', size=10),
                                hovertext=winners, hoverinfo='text'))
        fig.update_layout(
            height=1200, 
            width=1600, 
            showlegend=False, 
            margin=dict(l=20, r=20, t=40, b=20), 
            xaxis=dict(showticklabels=False), 
            yaxis=dict(showticklabels=False), 
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
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

    # Show current weights info
    if 'global_weights' in st.session_state:
        weights = st.session_state.global_weights
        st.info(f"Using global Elo weights. Form parameters: k={weights.form_k:.3f}, α={weights.form_alpha:.2f}")
    else:
        st.warning("No global weights set. Using default weights.")

    if st.button('Run Scorito Analysis'):
        with st.spinner(f'Running {num_simulations} simulations for Scorito analysis...'):
            sim = FixedDrawEloSimulator()
            
            # Apply global weights if available
            if 'global_weights' in st.session_state:
                try:
                    sim.set_custom_weights(st.session_state.global_weights)
                    weights = st.session_state.global_weights
                    st.success(f"Applied global Elo weights. Form parameters: k={weights.form_k:.3f}, α={weights.form_alpha:.2f}")
                except Exception as e:
                    st.warning(f"Could not apply global weights: {e}. Using default weights.")
            else:
                st.warning("No global weights set. Using default weights.")
            
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


def get_data_status(gender: str) -> Dict[str, any]:
    """Get the current status of data loading for the specified gender"""
    try:
        from tennis_simulator.data.data_loader import get_data_loader
        
        data_loader = get_data_loader()
        status = {
            'elo': data_loader.get_data_source(gender, 'elo') is not None,
            'yelo': data_loader.get_data_source(gender, 'yelo') is not None,
            'form': data_loader.get_data_source(gender, 'form') is not None,
            'tier': data_loader.get_data_source(gender, 'tier') is not None,
            'players_loaded': 0
        }
        
        # Try to get player count
        try:
            db = populate_static_database(gender)
            status['players_loaded'] = len(db)
        except:
            pass
        
        return status
        
    except Exception as e:
        print(f"Error getting data status for {gender}: {e}")
        return {
            'elo': False,
            'yelo': False,
            'form': False,
            'tier': False,
            'players_loaded': 0
        }


def display_data_status():
    """Display the current status of data loading"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Data Status")
    
    men_status = get_data_status('men')
    women_status = get_data_status('women')
    
    # Men's status
    st.sidebar.markdown("**Men's Data:**")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.sidebar.markdown(f"Elo: {'✅' if men_status['elo'] else '❌'}")
        st.sidebar.markdown(f"yElo: {'✅' if men_status['yelo'] else '❌'}")
    with col2:
        st.sidebar.markdown(f"Form: {'✅' if men_status['form'] else '❌'}")
        st.sidebar.markdown(f"Tier: {'✅' if men_status['tier'] else '❌'}")
    
    st.sidebar.markdown(f"Players: {men_status['players_loaded']}")
    
    # Women's status
    st.sidebar.markdown("**Women's Data:**")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.sidebar.markdown(f"Elo: {'✅' if women_status['elo'] else '❌'}")
        st.sidebar.markdown(f"yElo: {'✅' if women_status['yelo'] else '❌'}")
    with col2:
        st.sidebar.markdown(f"Form: {'✅' if women_status['form'] else '❌'}")
        st.sidebar.markdown(f"Tier: {'✅' if women_status['tier'] else '❌'}")
    
    st.sidebar.markdown(f"Players: {women_status['players_loaded']}")
    
    # Overall status
    if men_status['players_loaded'] == 0 and women_status['players_loaded'] == 0:
        st.sidebar.error("⚠️ No data loaded")
        st.sidebar.info("Check deployment guide for troubleshooting")
    elif men_status['players_loaded'] > 0 and women_status['players_loaded'] > 0:
        st.sidebar.success("✅ All data loaded successfully")
    else:
        st.sidebar.warning("⚠️ Partial data loaded")


def main():
    """Main dashboard function"""
    # Sidebar
    st.sidebar.title("🎾 Navigation")
    
    # Navigation
    page = st.sidebar.selectbox(
        "Select Page:",
        options=[
            '🏠 Overview', '📊 Database Overview', '🔍 Player Search', '🎾 Match Simulation', '⚖️ Elo Weights',
            '🏆 Single Tournament', '🔬 Explorer', '🎮 Scorito Game Analysis'
        ],
        index=0
    )
    
    # Page routing
    if page == '🏠 Overview':
        display_overview()
    elif page == '📊 Database Overview':
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
    
    elif page == '🔍 Player Search':
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
    
    elif page == '🎾 Match Simulation':
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
        
        display_match_simulation(db, gender)
    
    elif page == '⚖️ Elo Weights':
        display_elo_weights_config()
    
    elif page == '🏆 Single Tournament':
        display_single_tournament()
    
    elif page == '🔬 Explorer':
        display_explorer()
    
    elif page == '🎮 Scorito Game Analysis':
        display_scorito_game_analysis()


if __name__ == "__main__":
    main() 