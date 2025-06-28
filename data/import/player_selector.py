#!/usr/bin/env python3
"""
Player Selector for Scorito Tennis Game
This script helps you select 12 men and 12 women (3 from each tier) for your Scorito game.
"""

from tennis_simulator import TournamentSimulator, Gender, Tier
import json

def display_players_by_tier(simulator, gender):
    """Display all players organized by tier"""
    tiers = simulator.get_players_by_tier(gender)
    
    print(f"\n=== {gender.value.upper()} TOURNAMENT - PLAYER SELECTION ===")
    print("Select 3 players from each tier (A, B, C, D)")
    
    for tier in Tier:
        print(f"\n--- TIER {tier.value} ---")
        players = tiers[tier]
        
        for i, player in enumerate(players, 1):
            seeding_info = f"(#{player.seeding})" if player.seeding else "(unseeded)"
            print(f"{i:2d}. {player.get_clean_name()} {seeding_info} ({player.country})")
            
            # Show advancement chances for key rounds
            r32_chance = player.get_advancement_chance("R32")
            qf_chance = player.get_advancement_chance("QF")
            sf_chance = player.get_advancement_chance("SF")
            w_chance = player.get_advancement_chance("W")
            
            print(f"     R32: {r32_chance:.1%} | QF: {qf_chance:.1%} | SF: {sf_chance:.1%} | W: {w_chance:.1%}")

def get_user_selections(simulator, gender):
    """Get user selections for a specific gender"""
    tiers = simulator.get_players_by_tier(gender)
    selections = {}
    
    print(f"\n=== SELECTING {gender.value.upper()} PLAYERS ===")
    
    for tier in Tier:
        print(f"\n--- SELECT 3 PLAYERS FROM TIER {tier.value} ---")
        players = tiers[tier]
        
        # Display players
        for i, player in enumerate(players, 1):
            seeding_info = f"(#{player.seeding})" if player.seeding else "(unseeded)"
            print(f"{i:2d}. {player.get_clean_name()} {seeding_info} ({player.country})")
        
        # Get user selections
        selected_indices = []
        while len(selected_indices) < 3:
            try:
                choice = input(f"Enter player number (1-{len(players)}): ").strip()
                if choice.lower() == 'help':
                    print("Enter the number of the player you want to select.")
                    print("You need to select exactly 3 players from this tier.")
                    continue
                
                player_index = int(choice) - 1
                if 0 <= player_index < len(players) and player_index not in selected_indices:
                    selected_indices.append(player_index)
                    selected_player = players[player_index]
                    print(f"Selected: {selected_player.get_clean_name()}")
                else:
                    print("Invalid selection. Please choose a valid player number.")
            except ValueError:
                print("Please enter a valid number.")
            except KeyboardInterrupt:
                print("\nSelection cancelled.")
                return None
        
        # Store selections
        selections[tier] = [players[i].get_clean_name() for i in selected_indices]
    
    return selections

def save_selections(selections, filename="scorito_selections.json"):
    """Save selections to a JSON file"""
    with open(filename, 'w') as f:
        json.dump(selections, f, indent=2)
    print(f"\nSelections saved to {filename}")

def load_selections(filename="scorito_selections.json"):
    """Load selections from a JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def main():
    """Main function for player selection"""
    print("=== SCORITO TENNIS PLAYER SELECTOR ===")
    print("This tool helps you select players for your Scorito game.")
    
    # Initialize simulator
    simulator = TournamentSimulator("importdata_men.txt", "importdata_womens.txt")
    
    # Check if saved selections exist
    saved_selections = load_selections()
    if saved_selections:
        print("\nFound saved selections:")
        print(json.dumps(saved_selections, indent=2))
        
        use_saved = input("\nUse saved selections? (y/n): ").lower().strip()
        if use_saved == 'y':
            return saved_selections
    
    # Display all players
    display_players_by_tier(simulator, Gender.MEN)
    display_players_by_tier(simulator, Gender.WOMEN)
    
    # Get user selections
    all_selections = {}
    
    # Get men selections
    men_selections = get_user_selections(simulator, Gender.MEN)
    if men_selections is None:
        return None
    all_selections["men"] = men_selections
    
    # Get women selections
    women_selections = get_user_selections(simulator, Gender.WOMEN)
    if women_selections is None:
        return None
    all_selections["women"] = women_selections
    
    # Save selections
    save_selections(all_selections)
    
    # Display final selections
    print("\n=== YOUR FINAL SELECTIONS ===")
    for gender, gender_selections in all_selections.items():
        print(f"\n{gender.upper()}:")
        for tier, players in gender_selections.items():
            print(f"  Tier {tier}: {', '.join(players)}")
    
    return all_selections

if __name__ == "__main__":
    main() 