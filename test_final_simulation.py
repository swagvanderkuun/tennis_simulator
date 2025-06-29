#!/usr/bin/env python3
"""
Test script to verify that the final match is being simulated correctly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tennis_simulator.simulators.fixed_draw_elo_simulator import FixedDrawEloSimulator
from tennis_simulator.core.models import Round

def test_final_simulation():
    """Test that the final match is being simulated."""
    print("Testing final match simulation...")
    
    # Create simulator
    sim = FixedDrawEloSimulator()
    sim.setup_tournaments()
    
    # Simulate men's tournament
    print("\n=== MEN'S TOURNAMENT ===")
    men_winner = sim.simulate_tournament(sim.men_tournament)
    print(f"Winner: {men_winner.name}")
    
    # Check all matches
    print(f"\nTotal matches played: {len(sim.men_tournament.matches)}")
    
    # Group matches by round
    matches_by_round = {}
    for match in sim.men_tournament.matches:
        round_name = match.round.name
        if round_name not in matches_by_round:
            matches_by_round[round_name] = []
        matches_by_round[round_name].append(match)
    
    # Display all rounds
    for round_name in ['R64', 'R32', 'R16', 'QF', 'SF', 'F']:
        if round_name in matches_by_round:
            print(f"\n{round_name} ({len(matches_by_round[round_name])} matches):")
            for match in matches_by_round[round_name]:
                winner_name = match.winner.name if match.winner else "TBD"
                loser_name = match.loser.name if match.loser else "TBD"
                print(f"  {winner_name} def. {loser_name}")
        else:
            print(f"\n{round_name}: No matches")
    
    # Check if final match exists
    if 'F' in matches_by_round:
        final_match = matches_by_round['F'][0]
        print(f"\n✅ Final match found: {final_match.winner.name} def. {final_match.loser.name}")
    else:
        print("\n❌ No final match found!")
    
    # Simulate women's tournament
    print("\n=== WOMEN'S TOURNAMENT ===")
    women_winner = sim.simulate_tournament(sim.women_tournament)
    print(f"Winner: {women_winner.name}")
    
    # Check all matches
    print(f"\nTotal matches played: {len(sim.women_tournament.matches)}")
    
    # Group matches by round
    matches_by_round = {}
    for match in sim.women_tournament.matches:
        round_name = match.round.name
        if round_name not in matches_by_round:
            matches_by_round[round_name] = []
        matches_by_round[round_name].append(match)
    
    # Display all rounds
    for round_name in ['R64', 'R32', 'R16', 'QF', 'SF', 'F']:
        if round_name in matches_by_round:
            print(f"\n{round_name} ({len(matches_by_round[round_name])} matches):")
            for match in matches_by_round[round_name]:
                winner_name = match.winner.name if match.winner else "TBD"
                loser_name = match.loser.name if match.loser else "TBD"
                print(f"  {winner_name} def. {loser_name}")
        else:
            print(f"\n{round_name}: No matches")
    
    # Check if final match exists
    if 'F' in matches_by_round:
        final_match = matches_by_round['F'][0]
        print(f"\n✅ Final match found: {final_match.winner.name} def. {final_match.loser.name}")
    else:
        print("\n❌ No final match found!")

if __name__ == "__main__":
    test_final_simulation() 