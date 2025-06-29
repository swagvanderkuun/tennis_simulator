#!/usr/bin/env python3
"""
Test script for Scorito point calculation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tennis_simulator.simulators.fixed_draw_elo_simulator import FixedDrawEloSimulator
from tennis_simulator.core.models import Round

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
    return player.tier.value.upper()

def test_scorito_calculation():
    print("Testing Scorito point calculation...")
    
    # Parse scoring
    scoring, header = parse_scorito_scoring()
    print(f"Scoring data: {scoring}")
    
    # Create simulator and run one simulation
    sim = FixedDrawEloSimulator()
    sim.setup_tournaments()
    tournament = sim.men_tournament
    
    print(f"Tournament has {len(tournament.players)} players")
    
    # Run one simulation
    sim.simulate_tournament(tournament)
    
    # Check results
    print(f"\nTournament winner: {tournament.winner.name if tournament.winner else 'None'}")
    
    # Count players in each round
    round_counts = {}
    for round_enum in Round:
        players_in_round = [p for p in tournament.players if p.current_round == round_enum]
        round_counts[round_enum.value] = len(players_in_round)
        print(f"Players in {round_enum.value}: {len(players_in_round)}")
    
    # Calculate points for a few players
    print("\nSample player points:")
    for p in tournament.players[:10]:
        tier = get_player_tier(p)
        round_to_index = {'R1': 0, 'R2': 1, 'R3': 2, 'R4': 3, 'QF': 4, 'SF': 5, 'F': 6}
        round_index = round_to_index.get(p.current_round.value, 0)
        tier_scoring = scoring.get(tier, [0]*7)
        total_points = sum(tier_scoring[:round_index + 1]) if round_index >= 0 else 0
        
        print(f"{p.name}: Tier {tier}, Round {p.current_round.value}, Points {total_points}")

if __name__ == "__main__":
    test_scorito_calculation() 