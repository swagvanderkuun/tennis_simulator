#!/usr/bin/env python3
"""
Test script for the new Static Tournament Simulator
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tennis_simulator.simulators.static_tournament_simulator import StaticTournamentSimulator, run_static_tournament_simulation
from tennis_simulator.core.models import Gender, Tier


def test_single_simulation():
    """Test a single tournament simulation"""
    print("=== Single Tournament Simulation ===")
    
    # Create simulator for Wimbledon (grass court)
    simulator = StaticTournamentSimulator("Wimbledon", "grass")
    
    # Setup tournaments with 64 players each
    simulator.setup_tournaments(num_players=64)
    
    # Run single simulation
    result = simulator.run_single_simulation()
    
    print(f"Men's Winner: {result['men_winner']}")
    print(f"Women's Winner: {result['women_winner']}")
    print(f"Surface: {result['surface']}")
    
    # Show tournament details
    men_tournament = result['men_tournament']
    women_tournament = result['women_tournament']
    
    print(f"\nMen's Tournament: {len(men_tournament.players)} players")
    print(f"Women's Tournament: {len(women_tournament.players)} players")


def test_multiple_simulations():
    """Test multiple tournament simulations"""
    print("\n=== Multiple Tournament Simulations ===")
    
    # Run 100 simulations for faster testing
    simulator = StaticTournamentSimulator("Wimbledon", "grass")
    stats = simulator.run_multiple_simulations(num_simulations=100)
    
    print(f"Completed {stats['num_simulations']} simulations")
    print(f"Surface: {stats['surface']}")
    
    # Show top winners
    print("\nTop 3 Men's Winners:")
    men_winners = stats['men_winners']
    men_sorted = sorted(men_winners.items(), key=lambda x: x[1], reverse=True)
    for i, (player, count) in enumerate(men_sorted[:3]):
        prob = count / stats['num_simulations']
        print(f"  {i+1}. {player}: {prob:.1%}")
    
    print("\nTop 3 Women's Winners:")
    women_winners = stats['women_winners']
    women_sorted = sorted(women_winners.items(), key=lambda x: x[1], reverse=True)
    for i, (player, count) in enumerate(women_sorted[:3]):
        prob = count / stats['num_simulations']
        print(f"  {i+1}. {player}: {prob:.1%}")


def test_different_surfaces():
    """Test simulations on different surfaces"""
    print("\n=== Different Surface Simulations ===")
    
    surfaces = ['grass', 'clay', 'hard', 'overall']
    
    for surface in surfaces:
        print(f"\n--- {surface.upper()} COURT ---")
        
        simulator = StaticTournamentSimulator("Grand Slam", surface)
        stats = simulator.run_multiple_simulations(num_simulations=50)  # Fewer for speed
        
        if stats['men_most_likely_winner']:
            winner, count = stats['men_most_likely_winner']
            prob = count / stats['num_simulations']
            print(f"Men's most likely winner: {winner} ({prob:.1%})")
        
        if stats['women_most_likely_winner']:
            winner, count = stats['women_most_likely_winner']
            prob = count / stats['num_simulations']
            print(f"Women's most likely winner: {winner} ({prob:.1%})")


def test_player_recommendations():
    """Test player recommendations"""
    print("\n=== Player Recommendations ===")
    
    simulator = StaticTournamentSimulator("Wimbledon", "grass")
    
    # Get recommendations for different tiers
    for tier in [Tier.A, Tier.B, Tier.C]:
        print(f"\n--- Tier {tier.value} Players (Men) ---")
        recommendations = simulator.get_player_recommendations(Gender.MEN, tier, num_recommendations=3)
        
        for i, (player, details) in enumerate(recommendations):
            print(f"  {i+1}. {player.name}")
            print(f"     Elo: {details['elo']:.1f}")
            print(f"     Surface Rating: {details['surface_rating']:.1f}")
    
    # Women's recommendations
    print(f"\n--- Tier A Players (Women) ---")
    recommendations = simulator.get_player_recommendations(Gender.WOMEN, Tier.A, num_recommendations=3)
    
    for i, (player, details) in enumerate(recommendations):
        print(f"  {i+1}. {player.name}")
        print(f"     Elo: {details['elo']:.1f}")
        print(f"     Surface Rating: {details['surface_rating']:.1f}")


def test_custom_weights():
    """Test custom weight configurations"""
    print("\n=== Custom Weight Configurations ===")
    
    from tennis_simulator.simulators.elo_match_simulator import EloWeights
    
    # Test different weight configurations
    weight_configs = [
        ("Overall Focus", EloWeights(elo_weight=0.6, helo_weight=0.2, celo_weight=0.15, gelo_weight=0.05)),
        ("Grass Specialist", EloWeights(elo_weight=0.2, helo_weight=0.1, celo_weight=0.1, gelo_weight=0.6)),
        ("Higher Form Impact", EloWeights(elo_weight=0.45, helo_weight=0.25, celo_weight=0.20, gelo_weight=0.10, form_elo_cap=120.0)),
    ]
    
    for name, weights in weight_configs:
        print(f"\n--- {name} ---")
        
        simulator = StaticTournamentSimulator("Wimbledon", "grass")
        simulator.set_custom_weights(weights)
        
        stats = simulator.run_multiple_simulations(num_simulations=50)
        
        if stats['men_most_likely_winner']:
            winner, count = stats['men_most_likely_winner']
            prob = count / stats['num_simulations']
            print(f"Men's winner: {winner} ({prob:.1%})")


def test_convenience_function():
    """Test the convenience function"""
    print("\n=== Convenience Function Test ===")
    
    # Run a quick simulation using the convenience function
    simulator = run_static_tournament_simulation(
        num_simulations=50,
        tournament_name="French Open",
        surface="clay"
    )
    
    print("Convenience function completed successfully!")


if __name__ == "__main__":
    print("Static Tournament Simulator Test")
    print("=" * 50)
    
    try:
        test_single_simulation()
        test_multiple_simulations()
        test_different_surfaces()
        test_player_recommendations()
        test_custom_weights()
        test_convenience_function()
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc() 