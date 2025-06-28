#!/usr/bin/env python3
"""
Example Usage of Tennis Simulator for Scorito Game
This script demonstrates how to use the simulator for a specific game scenario.
"""

from tennis_simulator import TournamentSimulator, Gender, Tier
from advanced_simulator import AdvancedTournamentSimulator
import json

def example_basic_simulation():
    """Example of basic tournament simulation"""
    print("=== BASIC SIMULATION EXAMPLE ===")
    
    # Initialize simulator
    simulator = TournamentSimulator("importdata_men.txt", "importdata_womens.txt")
    
    # Example player selections (you would replace these with your actual selections)
    selected_players = {
        Gender.MEN: {
            Tier.A: ["Jannik Sinner", "Carlos Alcaraz", "Novak Djokovic"],
            Tier.B: ["Daniil Medvedev", "Alexander Zverev", "Taylor Fritz"],
            Tier.C: ["Tommy Paul", "Frances Tiafoe", "Ben Shelton"],
            Tier.D: ["Lorenzo Musetti", "Denis Shapovalov", "Grigor Dimitrov"]
        },
        Gender.WOMEN: {
            Tier.A: ["Iga Swiatek", "Coco Gauff", "Aryna Sabalenka"],
            Tier.B: ["Elena Rybakina", "Jessica Pegula", "Madison Keys"],
            Tier.C: ["Paula Badosa", "Donna Vekic", "Elina Svitolina"],
            Tier.D: ["Mirra Andreeva", "Emma Navarro", "Karolina Muchova"]
        }
    }
    
    # Simulate the game
    results = simulator.simulate_scorito_game(selected_players)
    
    print("\nSimulation Results:")
    total_points = 0
    for gender, gender_results in results.items():
        print(f"\n{gender.upper()}:")
        gender_total = 0
        for tier, points in gender_results.items():
            print(f"  {tier}: {points} points")
            gender_total += points
        print(f"  Total: {gender_total} points")
        total_points += gender_total
    
    print(f"\nGRAND TOTAL: {total_points} points")
    return results

def example_advanced_analysis():
    """Example of advanced statistical analysis"""
    print("\n=== ADVANCED ANALYSIS EXAMPLE ===")
    
    # Initialize advanced simulator
    simulator = AdvancedTournamentSimulator("importdata_men.txt", "importdata_womens.txt")
    
    # Get recommendations for men's tournament
    print("\nTop recommendations for Men's Tournament:")
    recommendations = simulator.get_player_recommendations(Gender.MEN, num_simulations=500)
    
    for tier in Tier:
        print(f"\nTier {tier.value} (Top 3):")
        for i, (player_name, expected_points) in enumerate(recommendations[tier][:3], 1):
            print(f"  {i}. {player_name}: {expected_points:.2f} expected points")
    
    # Run statistical analysis
    print("\nStatistical Analysis (Men's Tournament):")
    stats = simulator.simulate_multiple_tournaments(Gender.MEN, num_simulations=500)
    
    print("\nTier Performance:")
    for tier, tier_stats in stats["tier_stats"].items():
        print(f"  Tier {tier}: {tier_stats['avg_points']:.2f} avg points")
    
    return recommendations, stats

def example_optimal_selection():
    """Example of creating an optimal player selection based on recommendations"""
    print("\n=== OPTIMAL SELECTION EXAMPLE ===")
    
    # Initialize advanced simulator
    simulator = AdvancedTournamentSimulator("importdata_men.txt", "importdata_womens.txt")
    
    # Get recommendations for both tournaments
    men_recommendations = simulator.get_player_recommendations(Gender.MEN, num_simulations=500)
    women_recommendations = simulator.get_player_recommendations(Gender.WOMEN, num_simulations=500)
    
    # Create optimal selections (top 3 from each tier)
    optimal_selections = {
        Gender.MEN: {},
        Gender.WOMEN: {}
    }
    
    for tier in Tier:
        # Men's optimal selection
        optimal_selections[Gender.MEN][tier] = [
            player_name for player_name, _ in men_recommendations[tier][:3]
        ]
        
        # Women's optimal selection
        optimal_selections[Gender.WOMEN][tier] = [
            player_name for player_name, _ in women_recommendations[tier][:3]
        ]
    
    print("\nOptimal Player Selections (based on recommendations):")
    
    for gender in Gender:
        print(f"\n{gender.value.upper()}:")
        for tier in Tier:
            players = optimal_selections[gender][tier]
            print(f"  Tier {tier.value}: {', '.join(players)}")
    
    # Test the optimal selection
    basic_simulator = TournamentSimulator("importdata_men.txt", "importdata_womens.txt")
    optimal_results = basic_simulator.simulate_scorito_game(optimal_selections)
    
    print("\nOptimal Selection Results:")
    total_points = 0
    for gender, gender_results in optimal_results.items():
        print(f"\n{gender.upper()}:")
        gender_total = 0
        for tier, points in gender_results.items():
            print(f"  {tier}: {points} points")
            gender_total += points
        print(f"  Total: {gender_total} points")
        total_points += gender_total
    
    print(f"\nOPTIMAL GRAND TOTAL: {total_points} points")
    
    return optimal_selections, optimal_results

def example_multiple_simulations():
    """Example of running multiple simulations to understand variance"""
    print("\n=== MULTIPLE SIMULATIONS EXAMPLE ===")
    
    # Initialize simulator
    simulator = TournamentSimulator("importdata_men.txt", "importdata_womens.txt")
    
    # Example selections
    selected_players = {
        Gender.MEN: {
            Tier.A: ["Jannik Sinner", "Carlos Alcaraz", "Novak Djokovic"],
            Tier.B: ["Daniil Medvedev", "Alexander Zverev", "Taylor Fritz"],
            Tier.C: ["Tommy Paul", "Frances Tiafoe", "Ben Shelton"],
            Tier.D: ["Lorenzo Musetti", "Denis Shapovalov", "Grigor Dimitrov"]
        },
        Gender.WOMEN: {
            Tier.A: ["Iga Swiatek", "Coco Gauff", "Aryna Sabalenka"],
            Tier.B: ["Elena Rybakina", "Jessica Pegula", "Madison Keys"],
            Tier.C: ["Paula Badosa", "Donna Vekic", "Elina Svitolina"],
            Tier.D: ["Mirra Andreeva", "Emma Navarro", "Karolina Muchova"]
        }
    }
    
    # Run multiple simulations
    num_simulations = 100
    results = []
    
    print(f"Running {num_simulations} simulations...")
    
    for i in range(num_simulations):
        result = simulator.simulate_scorito_game(selected_players)
        total_points = sum(sum(gender_results.values()) for gender_results in result.values())
        results.append(total_points)
    
    # Analyze results
    results.sort()
    avg_points = sum(results) / len(results)
    min_points = min(results)
    max_points = max(results)
    median_points = results[len(results) // 2]
    
    print(f"\nSimulation Results ({num_simulations} runs):")
    print(f"  Average points: {avg_points:.1f}")
    print(f"  Minimum points: {min_points}")
    print(f"  Maximum points: {max_points}")
    print(f"  Median points: {median_points}")
    
    # Show distribution
    print(f"\nPoint Distribution:")
    ranges = [(0, 20), (21, 40), (41, 60), (61, 80), (81, 100), (101, 200)]
    for low, high in ranges:
        count = sum(1 for points in results if low <= points <= high)
        percentage = (count / len(results)) * 100
        print(f"  {low}-{high} points: {count} times ({percentage:.1f}%)")
    
    return results

def main():
    """Run all examples"""
    print("TENNIS SIMULATOR - EXAMPLE USAGE")
    print("=" * 50)
    
    # Run all examples
    basic_results = example_basic_simulation()
    recommendations, stats = example_advanced_analysis()
    optimal_selections, optimal_results = example_optimal_selection()
    simulation_results = example_multiple_simulations()
    
    print("\n" + "=" * 50)
    print("EXAMPLE COMPLETE!")
    print("\nKey takeaways:")
    print("1. Use the advanced simulator for recommendations")
    print("2. Run multiple simulations to understand variance")
    print("3. Consider both expected value and risk")
    print("4. Balance high-tier safety with low-tier upside")

if __name__ == "__main__":
    main() 