#!/usr/bin/env python3
"""
Debug script to trace the final round simulation.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tennis_simulator.simulators.fixed_draw_elo_simulator import FixedDrawEloSimulator
from tennis_simulator.core.models import Round

def debug_final_round():
    """Debug the final round simulation step by step."""
    print("Debugging final round simulation...")
    
    # Create simulator
    sim = FixedDrawEloSimulator()
    sim.setup_tournaments()
    
    # Simulate men's tournament step by step
    print("\n=== MEN'S TOURNAMENT DEBUG ===")
    tournament = sim.men_tournament
    tournament.reset()
    
    current_players = tournament.players.copy()
    round_name = Round.R64
    
    while len(current_players) > 1:
        print(f"\n--- {round_name.name} ---")
        print(f"Players: {len(current_players)}")
        print(f"First 4 players: {[p.name for p in current_players[:4]]}")
        
        # Create matches for current round
        matches = sim._create_matches_for_round(current_players, round_name)
        print(f"Created {len(matches)} matches")
        
        # Simulate matches
        winners = []
        for i, match in enumerate(matches):
            winner, loser, details = sim.match_simulator.simulate_match(match.player1, match.player2)
            match.winner = winner
            match.loser = loser
            tournament.matches.append(match)
            winners.append(winner)
            print(f"  Match {i+1}: {winner.name} def. {loser.name}")
        
        print(f"Winners: {[w.name for w in winners]}")
        
        # Update for next round
        current_players = winners
        round_name = sim._get_next_round(round_name)
        
        if round_name == Round.F:
            print(f"\n*** FINAL ROUND DEBUG ***")
            print(f"Final players: {[p.name for p in current_players]}")
            print(f"Final round name: {round_name}")
    
    # Set tournament winner
    if current_players:
        tournament.winner = current_players[0]
        tournament.completed = True
        print(f"\n🏆 Tournament Winner: {tournament.winner.name}")
    
    # Check final matches
    final_matches = [m for m in tournament.matches if m.round == Round.F]
    print(f"\nFinal matches found: {len(final_matches)}")
    for i, match in enumerate(final_matches):
        print(f"  Final match {i+1}: {match.winner.name} def. {match.loser.name}")

if __name__ == "__main__":
    debug_final_round() 