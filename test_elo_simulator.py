#!/usr/bin/env python3
"""
Test script for the new Elo-based match simulator
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tennis_simulator.core.models import Player, Tier
from tennis_simulator.simulators.elo_match_simulator import EloMatchSimulator, EloWeights, create_match_simulator


def create_test_players():
    """Create test players with different Elo ratings"""
    
    # Top tier players
    alcaraz = Player(
        name="Carlos Alcaraz",
        country="ESP",
        seeding=1,
        tier=Tier.A,
        elo=2246.5,
        helo=2129.0,
        celo=2203.5,
        gelo=2129.1,
        yelo=5.0,
        atp_rank=2
    )
    
    sinner = Player(
        name="Jannik Sinner", 
        country="ITA",
        seeding=2,
        tier=Tier.A,
        elo=2208.4,
        helo=2177.6,
        celo=2111.5,
        gelo=1955.8,
        yelo=3.0,
        atp_rank=1
    )
    
    djokovic = Player(
        name="Novak Djokovic",
        country="SRB", 
        seeding=3,
        tier=Tier.A,
        elo=2161.4,
        helo=2114.7,
        celo=2083.2,
        gelo=2037.2,
        yelo=8.0,
        atp_rank=6
    )
    
    # Mid tier player
    paul = Player(
        name="Tommy Paul",
        country="USA",
        seeding=12,
        tier=Tier.B,
        elo=2023.6,
        helo=2023.6,
        celo=2023.6,
        gelo=2023.6,
        yelo=9.0,
        atp_rank=15
    )
    
    # Lower tier player
    lower_player = Player(
        name="Lower Tier Player",
        country="XXX",
        seeding=None,
        tier=Tier.D,
        elo=1800.0,
        helo=1800.0,
        celo=1800.0,
        gelo=1800.0,
        yelo=10.0,
        atp_rank=100
    )
    
    return alcaraz, sinner, djokovic, paul, lower_player


def test_basic_simulation():
    """Test basic match simulation"""
    print("=== Basic Match Simulation ===")
    
    alcaraz, sinner, djokovic, paul, lower_player = create_test_players()
    
    # Create simulator with default weights
    simulator = EloMatchSimulator()
    
    # Test Alcaraz vs Sinner
    print(f"\nMatch: {alcaraz.name} vs {sinner.name}")
    winner, loser, details = simulator.simulate_match(alcaraz, sinner)
    print(f"Winner: {winner.name}")
    print(f"Win probability: {details['winner_probability']:.3f}")
    print(f"Rating difference: {details['rating_difference']:.1f}")
    
    # Test multiple simulations
    print(f"\nRunning 1000 simulations of {alcaraz.name} vs {sinner.name}:")
    alcaraz_wins = 0
    for _ in range(1000):
        winner, _, _ = simulator.simulate_match(alcaraz, sinner)
        if winner.name == alcaraz.name:
            alcaraz_wins += 1
    
    print(f"Alcaraz won {alcaraz_wins}/1000 matches ({alcaraz_wins/10:.1f}%)")


def test_surface_specific_weights():
    """Test surface-specific weight configurations"""
    print("\n=== Surface-Specific Weights ===")
    
    alcaraz, sinner, djokovic, paul, lower_player = create_test_players()
    
    surfaces = ['hard', 'clay', 'grass', 'overall']
    
    for surface in surfaces:
        print(f"\n--- {surface.upper()} COURT ---")
        simulator = create_match_simulator(surface=surface)
        
        # Show weights
        weights = simulator.weights
        print(f"Weights: Elo={weights.elo_weight}, hElo={weights.helo_weight}, "
              f"cElo={weights.celo_weight}, gElo={weights.gelo_weight}")
        
        # Test Alcaraz vs Sinner
        winner, loser, details = simulator.simulate_match(alcaraz, sinner)
        print(f"{alcaraz.name} vs {sinner.name}: {winner.name} wins (prob: {details['winner_probability']:.3f})")
        
        # Test weighted ratings
        alcaraz_rating = simulator.calculate_weighted_rating(alcaraz)
        sinner_rating = simulator.calculate_weighted_rating(sinner)
        print(f"Weighted ratings: {alcaraz.name}={alcaraz_rating:.1f}, {sinner.name}={sinner_rating:.1f}")


def test_custom_weights():
    """Test custom weight configurations"""
    print("\n=== Custom Weight Configurations ===")
    
    alcaraz, sinner, djokovic, paul, lower_player = create_test_players()
    
    # Test different weight configurations
    weight_configs = [
        ("Overall Elo Focus", EloWeights(elo_weight=0.8, helo_weight=0.1, celo_weight=0.05, gelo_weight=0.05)),
        ("Hard Court Specialist", EloWeights(elo_weight=0.2, helo_weight=0.6, celo_weight=0.15, gelo_weight=0.05)),
        ("Clay Court Specialist", EloWeights(elo_weight=0.2, helo_weight=0.1, celo_weight=0.6, gelo_weight=0.1)),
        # yElo removed; mimic "more reactive" behavior by increasing form cap.
        ("Higher Form Impact", EloWeights(elo_weight=0.45, helo_weight=0.25, celo_weight=0.20, gelo_weight=0.10, form_elo_cap=120.0)),
    ]
    
    for name, weights in weight_configs:
        print(f"\n--- {name} ---")
        simulator = EloMatchSimulator(weights=weights)
        
        # Test Alcaraz vs Sinner
        winner, loser, details = simulator.simulate_match(alcaraz, sinner)
        print(f"{alcaraz.name} vs {sinner.name}: {winner.name} wins (prob: {details['winner_probability']:.3f})")
        
        # Show weighted ratings
        alcaraz_rating = simulator.calculate_weighted_rating(alcaraz)
        sinner_rating = simulator.calculate_weighted_rating(sinner)
        print(f"Weighted ratings: {alcaraz.name}={alcaraz_rating:.1f}, {sinner.name}={sinner_rating:.1f}")


def test_win_probability_calculation():
    """Test win probability calculations"""
    print("\n=== Win Probability Calculations ===")
    
    alcaraz, sinner, djokovic, paul, lower_player = create_test_players()
    
    simulator = EloMatchSimulator()
    
    matchups = [
        (alcaraz, sinner, "Alcaraz vs Sinner"),
        (alcaraz, djokovic, "Alcaraz vs Djokovic"),
        (alcaraz, paul, "Alcaraz vs Paul"),
        (alcaraz, lower_player, "Alcaraz vs Lower Player"),
        (sinner, djokovic, "Sinner vs Djokovic"),
        (paul, lower_player, "Paul vs Lower Player"),
    ]
    
    for player1, player2, description in matchups:
        prob = simulator.calculate_win_probability(player1, player2)
        print(f"{description}: {player1.name} win probability = {prob:.3f} ({prob*100:.1f}%)")


def test_rating_differences():
    """Test how rating differences affect win probabilities"""
    print("\n=== Rating Difference Analysis ===")
    
    alcaraz, sinner, djokovic, paul, lower_player = create_test_players()
    
    simulator = EloMatchSimulator()
    
    # Create a range of rating differences
    base_rating = 2000.0
    differences = [0, 50, 100, 200, 400, 600, 800]
    
    print("Rating Difference | Win Probability")
    print("-" * 35)
    
    for diff in differences:
        # Create two players with specific rating difference
        player1 = Player(
            name="Player A",
            country="XXX",
            seeding=1,
            tier=Tier.A,
            elo=base_rating,
            helo=base_rating,
            celo=base_rating,
            gelo=base_rating,
            yelo=10.0,
            atp_rank=1
        )
        
        player2 = Player(
            name="Player B", 
            country="XXX",
            seeding=2,
            tier=Tier.A,
            elo=base_rating + diff,
            helo=base_rating + diff,
            celo=base_rating + diff,
            gelo=base_rating + diff,
            yelo=10.0,
            atp_rank=2
        )
        
        prob = simulator.calculate_win_probability(player1, player2)
        print(f"{diff:>15} | {prob:.3f} ({prob*100:.1f}%)")


if __name__ == "__main__":
    print("Elo-based Tennis Match Simulator Test")
    print("=" * 50)
    
    test_basic_simulation()
    test_surface_specific_weights()
    test_custom_weights()
    test_win_probability_calculation()
    test_rating_differences()
    
    print("\n" + "=" * 50)
    print("Test completed!") 