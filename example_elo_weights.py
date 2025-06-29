#!/usr/bin/env python3
"""
Example script demonstrating how to configure Elo weights for different scenarios.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tennis_simulator.core.models import Player, Tier
from tennis_simulator.simulators.elo_match_simulator import EloMatchSimulator, EloWeights, create_match_simulator


def create_sample_players():
    """Create sample players for demonstration"""
    
    # Create players with different strengths on different surfaces
    nadal = Player(
        name="Rafael Nadal",
        country="ESP",
        seeding=1,
        tier=Tier.A,
        elo=2100.0,      # Overall strong
        helo=2000.0,     # Good on hard
        celo=2300.0,     # Excellent on clay
        gelo=1800.0,     # Weaker on grass
        yelo=8.0,        # Recent form
        atp_rank=5
    )
    
    federer = Player(
        name="Roger Federer",
        country="SUI", 
        seeding=2,
        tier=Tier.A,
        elo=2100.0,      # Overall strong
        helo=2200.0,     # Excellent on hard
        celo=1900.0,     # Good on clay
        gelo=2300.0,     # Excellent on grass
        yelo=6.0,        # Recent form
        atp_rank=10
    )
    
    return nadal, federer


def demonstrate_surface_specific_weights():
    """Demonstrate how surface-specific weights affect match outcomes"""
    print("=== Surface-Specific Weight Demonstration ===")
    
    nadal, federer = create_sample_players()
    
    surfaces = ['hard', 'clay', 'grass', 'overall']
    
    for surface in surfaces:
        print(f"\n--- {surface.upper()} COURT ---")
        
        # Create simulator for specific surface
        simulator = create_match_simulator(surface=surface)
        
        # Show the weights being used
        weights = simulator.weights
        print(f"Weights: Elo={weights.elo_weight:.1f}, hElo={weights.helo_weight:.1f}, "
              f"cElo={weights.celo_weight:.1f}, gElo={weights.gelo_weight:.1f}, yElo={weights.yelo_weight:.1f}")
        
        # Calculate weighted ratings
        nadal_rating = simulator.calculate_weighted_rating(nadal)
        federer_rating = simulator.calculate_weighted_rating(federer)
        
        print(f"Nadal weighted rating: {nadal_rating:.1f}")
        print(f"Federer weighted rating: {federer_rating:.1f}")
        
        # Calculate win probability
        nadal_win_prob = simulator.calculate_win_probability(nadal, federer)
        print(f"Nadal win probability: {nadal_win_prob:.3f} ({nadal_win_prob*100:.1f}%)")
        
        # Simulate a match
        winner, loser, details = simulator.simulate_match(nadal, federer)
        print(f"Match result: {winner.name} defeats {loser.name}")


def demonstrate_custom_weight_configurations():
    """Demonstrate custom weight configurations"""
    print("\n=== Custom Weight Configuration Examples ===")
    
    nadal, federer = create_sample_players()
    
    # Define different weight configurations
    weight_configs = [
        {
            "name": "Overall Performance Focus",
            "weights": EloWeights(elo_weight=0.6, helo_weight=0.15, celo_weight=0.15, gelo_weight=0.05, yelo_weight=0.05),
            "description": "Heavily weights overall Elo rating"
        },
        {
            "name": "Recent Form Focus", 
            "weights": EloWeights(elo_weight=0.2, helo_weight=0.2, celo_weight=0.2, gelo_weight=0.2, yelo_weight=0.2),
            "description": "Equal weight to all factors including recent form"
        },
        {
            "name": "Surface Specialist",
            "weights": EloWeights(elo_weight=0.1, helo_weight=0.3, celo_weight=0.3, gelo_weight=0.3, yelo_weight=0.0),
            "description": "Focuses on surface-specific ratings, ignores recent form"
        },
        {
            "name": "Hard Court Tournament",
            "weights": EloWeights(elo_weight=0.2, helo_weight=0.5, celo_weight=0.1, gelo_weight=0.1, yelo_weight=0.1),
            "description": "Optimized for hard court tournaments"
        },
        {
            "name": "Clay Court Tournament",
            "weights": EloWeights(elo_weight=0.2, helo_weight=0.1, celo_weight=0.5, gelo_weight=0.1, yelo_weight=0.1),
            "description": "Optimized for clay court tournaments"
        },
        {
            "name": "Grass Court Tournament", 
            "weights": EloWeights(elo_weight=0.2, helo_weight=0.1, celo_weight=0.1, gelo_weight=0.5, yelo_weight=0.1),
            "description": "Optimized for grass court tournaments"
        }
    ]
    
    for config in weight_configs:
        print(f"\n--- {config['name']} ---")
        print(f"Description: {config['description']}")
        
        # Create simulator with custom weights
        simulator = EloMatchSimulator(weights=config['weights'])
        
        # Show weights
        weights = simulator.weights
        print(f"Weights: Elo={weights.elo_weight:.1f}, hElo={weights.helo_weight:.1f}, "
              f"cElo={weights.celo_weight:.1f}, gElo={weights.gelo_weight:.1f}, yElo={weights.yelo_weight:.1f}")
        
        # Calculate weighted ratings
        nadal_rating = simulator.calculate_weighted_rating(nadal)
        federer_rating = simulator.calculate_weighted_rating(federer)
        
        print(f"Nadal weighted rating: {nadal_rating:.1f}")
        print(f"Federer weighted rating: {federer_rating:.1f}")
        
        # Calculate win probability
        nadal_win_prob = simulator.calculate_win_probability(nadal, federer)
        print(f"Nadal win probability: {nadal_win_prob:.3f} ({nadal_win_prob*100:.1f}%)")


def demonstrate_weight_validation():
    """Demonstrate weight validation"""
    print("\n=== Weight Validation Examples ===")
    
    # Valid weights (sum to 1.0)
    try:
        valid_weights = EloWeights(elo_weight=0.4, helo_weight=0.3, celo_weight=0.2, gelo_weight=0.05, yelo_weight=0.05)
        print("✓ Valid weights created successfully")
    except ValueError as e:
        print(f"✗ Error with valid weights: {e}")
    
    # Invalid weights (don't sum to 1.0)
    try:
        invalid_weights = EloWeights(elo_weight=0.5, helo_weight=0.5, celo_weight=0.5, gelo_weight=0.5, yelo_weight=0.5)
        print("✗ Invalid weights should have failed")
    except ValueError as e:
        print(f"✓ Correctly caught invalid weights: {e}")


def demonstrate_factory_functions():
    """Demonstrate the factory functions for creating simulators"""
    print("\n=== Factory Function Examples ===")
    
    nadal, federer = create_sample_players()
    
    # Create simulator using surface
    print("Creating simulator for clay court...")
    clay_simulator = create_match_simulator(surface='clay')
    clay_weights = clay_simulator.weights
    print(f"Clay weights: Elo={clay_weights.elo_weight:.1f}, hElo={clay_weights.helo_weight:.1f}, "
          f"cElo={clay_weights.celo_weight:.1f}, gElo={clay_weights.gelo_weight:.1f}, yElo={clay_weights.yelo_weight:.1f}")
    
    # Create simulator using custom weights
    print("\nCreating simulator with custom weights...")
    custom_weights = EloWeights(elo_weight=0.3, helo_weight=0.4, celo_weight=0.1, gelo_weight=0.1, yelo_weight=0.1)
    custom_simulator = create_match_simulator(weights=custom_weights)
    print(f"Custom weights applied successfully")
    
    # Test both simulators
    clay_prob = clay_simulator.calculate_win_probability(nadal, federer)
    custom_prob = custom_simulator.calculate_win_probability(nadal, federer)
    
    print(f"Clay court simulator - Nadal win probability: {clay_prob:.3f}")
    print(f"Custom simulator - Nadal win probability: {custom_prob:.3f}")


def show_usage_examples():
    """Show practical usage examples"""
    print("\n=== Practical Usage Examples ===")
    
    print("""
# Example 1: Wimbledon (Grass Court)
wimbledon_simulator = create_match_simulator(surface='grass')

# Example 2: French Open (Clay Court)  
french_open_simulator = create_match_simulator(surface='clay')

# Example 3: US Open (Hard Court)
us_open_simulator = create_match_simulator(surface='hard')

# Example 4: Custom weights for a specific tournament
custom_weights = EloWeights(
    elo_weight=0.3,    # 30% overall performance
    helo_weight=0.25,  # 25% hard court performance
    celo_weight=0.25,  # 25% clay court performance  
    gelo_weight=0.1,   # 10% grass court performance
    yelo_weight=0.1    # 10% recent form
)
custom_simulator = create_match_simulator(weights=custom_weights)

# Example 5: Recent form focus
recent_form_weights = EloWeights(
    elo_weight=0.2,
    helo_weight=0.2, 
    celo_weight=0.2,
    gelo_weight=0.2,
    yelo_weight=0.2  # Equal weight to recent form
)
recent_simulator = create_match_simulator(weights=recent_form_weights)
    """)


if __name__ == "__main__":
    print("Elo Weight Configuration Examples")
    print("=" * 50)
    
    demonstrate_surface_specific_weights()
    demonstrate_custom_weight_configurations()
    demonstrate_weight_validation()
    demonstrate_factory_functions()
    show_usage_examples()
    
    print("\n" + "=" * 50)
    print("Examples completed!") 