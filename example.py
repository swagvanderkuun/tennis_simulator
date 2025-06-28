#!/usr/bin/env python3
"""
Example usage of the Tennis Simulator package.

This script demonstrates the main features of the tennis tournament simulator.
"""

from src.tennis_simulator import (
    FixedDrawSimulator, run_tournament_simulation,
    player_db, PlayerSelector, Gender, Tier, ScoritoGame
)

def main():
    print("🎾 Tennis Tournament Simulator - Example Usage")
    print("=" * 50)
    
    # 1. Database operations
    print("\n1. Database Operations")
    print("-" * 20)
    
    # Get players by gender
    men_players = player_db.get_players_by_gender(Gender.MEN)
    women_players = player_db.get_players_by_gender(Gender.WOMEN)
    
    print(f"Total men's players: {len(men_players)}")
    print(f"Total women's players: {len(women_players)}")
    
    # Get players by tier
    men_tier_a = player_db.get_players_by_tier(Gender.MEN, Tier.A)
    women_tier_a = player_db.get_players_by_tier(Gender.WOMEN, Tier.A)
    
    print(f"Men's A-tier players: {len(men_tier_a)}")
    print(f"Women's A-tier players: {len(women_tier_a)}")
    
    # Print some example players
    print("\nExample A-tier players:")
    for player in list(men_tier_a)[:3]:
        print(f"  {player.name} ({player.country}) - Elo: {player.elo}, yElo: {player.yelo}")
    
    # 2. Tournament simulation
    print("\n2. Tournament Simulation")
    print("-" * 20)
    
    # Create simulator
    simulator = FixedDrawSimulator("Wimbledon")
    
    # Setup tournaments with all players (these are now created from import data)
    simulator.setup_tournaments([], [])
    
    # Show first round draw for men
    print("\nMen's R64 Draw:")
    men_draw = list(simulator.men_tournament.players)
    for i in range(0, len(men_draw), 2):
        if i+1 < len(men_draw):
            print(f"  {men_draw[i].name} vs {men_draw[i+1].name}")
        else:
            print(f"  {men_draw[i].name} (bye)")
    
    # Show first round draw for women
    print("\nWomen's R64 Draw:")
    women_draw = list(simulator.women_tournament.players)
    for i in range(0, len(women_draw), 2):
        if i+1 < len(women_draw):
            print(f"  {women_draw[i].name} vs {women_draw[i+1].name}")
        else:
            print(f"  {women_draw[i].name} (bye)")
    
    # Run single simulation
    print("\nRunning single simulation...")
    result = simulator.run_single_simulation()
    
    print(f"Men's winner: {result['men_winner']}")
    print(f"Women's winner: {result['women_winner']}")
    print(f"Men's finalists: {result['men_finalists']}")
    print(f"Women's finalists: {result['women_finalists']}")
    
    # 3. Multiple simulations
    print("\n3. Multiple Simulations")
    print("-" * 20)
    
    print("Running 100 simulations for statistics...")
    stats = simulator.run_multiple_simulations(100)
    
    print(f"Total simulations: {stats['total_simulations']}")
    print("\nTop 5 men's win probabilities:")
    for player, prob in list(stats['men_win_probabilities'].items())[:5]:
        print(f"  {player}: {prob*100:.1f}%")
    
    print("\nTop 5 women's win probabilities:")
    for player, prob in list(stats['women_win_probabilities'].items())[:5]:
        print(f"  {player}: {prob*100:.1f}%")
    
    # 4. Player recommendations
    print("\n4. Player Recommendations")
    print("-" * 20)
    
    # Get recommendations for men's A-tier
    recommendations = simulator.get_player_recommendations(
        Gender.MEN, Tier.A, num_recommendations=3
    )
    
    print("Top 3 men's A-tier recommendations:")
    for i, (player, stats) in enumerate(recommendations, 1):
        print(f"  {i}. {player.name}: {stats['expected_points']:.1f} expected points "
              f"({stats['win_rate']:.1f}% win rate)")
    
    # 5. Player selection
    print("\n5. Player Selection")
    print("-" * 20)
    
    # Create a Scorito game
    game = ScoritoGame("Example Game")
    
    # Add some example selections (you would normally do this interactively)
    men_a_players = list(men_tier_a)[:3]
    women_a_players = list(women_tier_a)[:3]
    
    # Add player selections
    game.add_player_selection(Gender.MEN, Tier.A, [p.name for p in men_a_players])
    game.add_player_selection(Gender.WOMEN, Tier.A, [p.name for p in women_a_players])
    
    print(f"Created Scorito game with {len(men_a_players) + len(women_a_players)} players")
    print(f"Men A-tier: {[p.name for p in men_a_players]}")
    print(f"Women A-tier: {[p.name for p in women_a_players]}")
    
    # 6. Simulate Scorito game
    print("\n6. Scorito Game Simulation")
    print("-" * 20)
    
    game_result = simulator.simulate_scorito_game(game)
    
    print(f"Simulation result:")
    print(f"  Men's winner: {game_result['simulation_result']['men_winner']}")
    print(f"  Women's winner: {game_result['simulation_result']['women_winner']}")
    print(f"  Scorito points: {game_result['scorito_points']}")
    print(f"  Total points: {game_result['total_points']}")
    
    # 7. Database operations
    print("\n7. Advanced Database Operations")
    print("-" * 20)
    
    # Update a player's tier
    if men_players:
        first_player = list(men_players.values())[0]
        print(f"Updating {first_player.name} from {first_player.tier.value} to B-tier...")
        player_db.update_player_tier(first_player.name, Gender.MEN, Tier.B)
        
        # Verify the change
        updated_player = men_players[first_player.name]
        print(f"Updated: {updated_player.name} is now {updated_player.tier.value}-tier")
    
    # Print players by tier
    print("\nPlayers by tier:")
    for tier in [Tier.A, Tier.B, Tier.C, Tier.D]:
        men_count = len(player_db.get_players_by_tier(Gender.MEN, tier))
        women_count = len(player_db.get_players_by_tier(Gender.WOMEN, tier))
        print(f"  {tier.value}-tier: {men_count} men, {women_count} women")
    
    print("\n✅ Example completed successfully!")


if __name__ == "__main__":
    main() 