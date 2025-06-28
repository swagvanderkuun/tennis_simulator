"""
Player selector utility for interactive player selection.
"""

import json
from typing import Dict, List, Optional
from pathlib import Path

from ..core.models import Gender, Tier, ScoritoGame
from ..data.player_database import player_db


class PlayerSelector:
    """Interactive player selector for Scorito games."""
    
    def __init__(self):
        self.selections: Dict[str, Dict[Tier, List[str]]] = {
            "men": {},
            "women": {}
        }
    
    def display_players_by_tier(self, gender: Gender) -> None:
        """Display all players organized by tier."""
        print(f"\n{gender.value.upper()} PLAYERS BY TIER:")
        print("=" * 60)
        
        for tier in Tier:
            players = player_db.get_players_by_tier(gender, tier)
            if players:
                print(f"\nTIER {tier.value}:")
                print("-" * 30)
                for i, player in enumerate(sorted(players, key=lambda p: p.get_primary_rank() or 999), 1):
                    elo_info = f" [Elo: {player.get_best_elo():.0f}]" if player.get_best_elo() else ""
                    rank_info = f" (Rank: {player.get_primary_rank()})" if player.get_primary_rank() else ""
                    print(f"{i:2d}. {player.name} ({player.country}){rank_info}{elo_info}")
    
    def select_players_for_tier(self, gender: Gender, tier: Tier) -> List[str]:
        """Select 3 players for a specific tier."""
        players = player_db.get_players_by_tier(gender, tier)
        if not players:
            print(f"No players found for {gender.value} Tier {tier.value}")
            return []
        
        print(f"\nSelect 3 players for {gender.value} Tier {tier.value}:")
        print("-" * 50)
        
        # Display players with numbers
        for i, player in enumerate(sorted(players, key=lambda p: p.get_primary_rank() or 999), 1):
            elo_info = f" [Elo: {player.get_best_elo():.0f}]" if player.get_best_elo() else ""
            rank_info = f" (Rank: {player.get_primary_rank()})" if player.get_primary_rank() else ""
            print(f"{i:2d}. {player.name} ({player.country}){rank_info}{elo_info}")
        
        selected_players = []
        sorted_players = sorted(players, key=lambda p: p.get_primary_rank() or 999)
        
        while len(selected_players) < 3:
            try:
                choice = input(f"\nEnter player number ({len(selected_players) + 1}/3): ").strip()
                if choice.lower() == 'quit':
                    return []
                
                player_num = int(choice)
                if 1 <= player_num <= len(sorted_players):
                    selected_player = sorted_players[player_num - 1]
                    if selected_player.name not in selected_players:
                        selected_players.append(selected_player.name)
                        print(f"Selected: {selected_player.name}")
                    else:
                        print("Player already selected. Choose another player.")
                else:
                    print(f"Please enter a number between 1 and {len(sorted_players)}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\nSelection cancelled.")
                return []
        
        return selected_players
    
    def interactive_selection(self) -> Dict[str, Dict[Tier, List[str]]]:
        """Run interactive player selection for both genders."""
        print("TENNIS PLAYER SELECTOR")
        print("=" * 50)
        print("Select 3 players from each tier for both men and women.")
        print("Type 'quit' at any time to exit.\n")
        
        for gender in [Gender.MEN, Gender.WOMEN]:
            print(f"\n{'='*20} {gender.value.upper()} {'='*20}")
            
            # Show all players first
            self.display_players_by_tier(gender)
            
            # Select players for each tier
            for tier in Tier:
                selected = self.select_players_for_tier(gender, tier)
                if not selected:  # User quit
                    return {}
                
                self.selections[gender.value][tier] = selected
                print(f"\nSelected for {gender.value} Tier {tier.value}: {', '.join(selected)}")
        
        return self.selections
    
    def display_selection_summary(self) -> None:
        """Display a summary of current selections."""
        if not self.selections["men"] and not self.selections["women"]:
            print("No selections made yet.")
            return
        
        print("\nSELECTION SUMMARY")
        print("=" * 50)
        
        for gender in ["men", "women"]:
            if self.selections[gender]:
                print(f"\n{gender.upper()}:")
                for tier in Tier:
                    if tier in self.selections[gender]:
                        players = self.selections[gender][tier]
                        print(f"  Tier {tier.value}: {', '.join(players)}")
    
    def save_selection(self, filename: str) -> bool:
        """Save current selection to a JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump(self.selections, f, indent=2)
            print(f"Selection saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving selection: {e}")
            return False
    
    def load_selection(self, filename: str) -> bool:
        """Load selection from a JSON file."""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Validate structure
            if "men" in data and "women" in data:
                self.selections = data
                print(f"Selection loaded from {filename}")
                return True
            else:
                print("Invalid selection file format")
                return False
        except Exception as e:
            print(f"Error loading selection: {e}")
            return False
    
    def create_scorito_game(self, game_name: str = "My Scorito Game") -> ScoritoGame:
        """Create a ScoritoGame object from current selections."""
        game = ScoritoGame(name=game_name)
        
        for gender in ["men", "women"]:
            for tier, players in self.selections[gender].items():
                game.add_player_selection(
                    Gender.MEN if gender == "men" else Gender.WOMEN,
                    Tier(tier),
                    players
                )
        
        return game
    
    def validate_selection(self) -> bool:
        """Validate that selection is complete (3 players per tier per gender)."""
        for gender in ["men", "women"]:
            for tier in Tier:
                if tier not in self.selections[gender]:
                    print(f"Missing {gender} Tier {tier.value} selection")
                    return False
                
                players = self.selections[gender][tier]
                if len(players) != 3:
                    print(f"Need exactly 3 players for {gender} Tier {tier.value}, got {len(players)}")
                    return False
        
        return True
    
    def get_player_stats(self, gender: Gender, player_name: str) -> Optional[Dict]:
        """Get statistics for a specific player."""
        player = player_db.get_player_by_name(player_name, gender)
        if not player:
            return None
        
        return {
            "name": player.name,
            "country": player.country,
            "tier": player.tier.value,
            "seeding": player.seeding,
            "elo": player.get_best_elo(),
            "grass_elo": player.get_grass_elo(),
            "rank": player.get_primary_rank(),
            "is_seeded": player.is_seeded()
        }


def run_interactive_selector() -> PlayerSelector:
    """Run the interactive player selector."""
    selector = PlayerSelector()
    
    try:
        selections = selector.interactive_selection()
        if selections:
            selector.display_selection_summary()
            
            # Ask if user wants to save
            save_choice = input("\nSave this selection? (y/n): ").strip().lower()
            if save_choice in ['y', 'yes']:
                filename = input("Enter filename (default: selection.json): ").strip()
                if not filename:
                    filename = "selection.json"
                selector.save_selection(filename)
        
        return selector
    
    except KeyboardInterrupt:
        print("\nSelection cancelled.")
        return selector


def load_and_validate_selection(filename: str) -> Optional[PlayerSelector]:
    """Load and validate a saved selection."""
    selector = PlayerSelector()
    
    if selector.load_selection(filename):
        if selector.validate_selection():
            selector.display_selection_summary()
            return selector
        else:
            print("Selection validation failed.")
            return None
    else:
        return None


# Example usage functions
def example_selection_workflow():
    """Example of how to use the player selector."""
    print("TENNIS PLAYER SELECTOR EXAMPLE")
    print("=" * 40)
    
    # Run interactive selection
    selector = run_interactive_selector()
    
    if selector.validate_selection():
        # Create Scorito game
        game = selector.create_scorito_game("Example Game")
        print(f"\nCreated Scorito game: {game}")
        
        # Show player stats for selected players
        print("\nPLAYER STATISTICS:")
        print("-" * 30)
        
        for gender in ["men", "women"]:
            for tier, players in selector.selections[gender].items():
                print(f"\n{gender.upper()} Tier {tier}:")
                for player_name in players:
                    stats = selector.get_player_stats(
                        Gender.MEN if gender == "men" else Gender.WOMEN,
                        player_name
                    )
                    if stats:
                        print(f"  {stats['name']}: Elo {stats['elo']:.0f}, Rank {stats['rank']}")
    else:
        print("Selection incomplete. Please try again.")


if __name__ == "__main__":
    example_selection_workflow() 