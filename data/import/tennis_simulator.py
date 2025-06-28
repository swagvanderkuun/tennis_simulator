import random
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class Gender(Enum):
    MEN = "men"
    WOMEN = "women"

class Tier(Enum):
    A = "A"
    B = "B" 
    C = "C"
    D = "D"

@dataclass
class Player:
    name: str
    country: str
    seeding: Optional[int]
    advancement_chances: Dict[str, float]  # R64, R32, R16, QF, SF, F, W
    current_round: str = "R64"
    eliminated: bool = False
    
    def get_advancement_chance(self, round_name: str) -> float:
        """Get the chance of advancing to the specified round"""
        return self.advancement_chances.get(round_name, 0.0)
    
    def get_clean_name(self) -> str:
        """Get player name without seeding information"""
        # Remove seeding pattern like "(1)" or "(32)" from the beginning
        clean_name = re.sub(r'^\(\d+\)', '', self.name).strip()
        return clean_name

@dataclass
class Match:
    player1: Player
    player2: Player
    winner: Optional[Player] = None
    
    def simulate(self) -> Player:
        """Simulate a match between two players based on their advancement chances"""
        if self.player1.eliminated:
            return self.player2
        if self.player2.eliminated:
            return self.player1
            
        # Get current round for both players
        current_round = self.player1.current_round
        
        # Get advancement chances for next round
        next_round_map = {
            "R64": "R32",
            "R32": "R16", 
            "R16": "QF",
            "QF": "SF",
            "SF": "F",
            "F": "W"
        }
        next_round = next_round_map.get(current_round, "W")
        
        chance1 = self.player1.get_advancement_chance(next_round)
        chance2 = self.player2.get_advancement_chance(next_round)
        
        # Normalize chances (they might not sum to 100% due to different paths)
        total_chance = chance1 + chance2
        if total_chance > 0:
            normalized_chance1 = chance1 / total_chance
        else:
            normalized_chance1 = 0.5
            
        # Simulate the match
        if random.random() < normalized_chance1:
            winner = self.player1
            self.player2.eliminated = True
        else:
            winner = self.player2
            self.player1.eliminated = True
            
        # Update winner's current round
        winner.current_round = next_round
        
        self.winner = winner
        return winner

class TournamentSimulator:
    def __init__(self, men_data_file: str, women_data_file: str):
        self.men_players = self._parse_player_data(men_data_file, Gender.MEN)
        self.women_players = self._parse_player_data(women_data_file, Gender.WOMEN)
        self.men_draw = self._create_draw(self.men_players)
        self.women_draw = self._create_draw(self.women_players)
        
    def _parse_player_data(self, filename: str, gender: Gender) -> List[Player]:
        """Parse player data from the import file"""
        players = []
        
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
        # Skip header lines
        data_lines = [line for line in lines if line.strip() and not line.startswith('2025') and not line.startswith('Player')]
        
        for line in data_lines:
            if line.strip() and not line.startswith('  	'):
                # Parse player line
                parts = line.strip().split('\t')
                if len(parts) >= 8:
                    player_info = parts[0].strip()
                    chances = [float(part.strip('%')) / 100.0 for part in parts[1:8] if part.strip()]
                    
                    # Extract seeding and name
                    seeding_match = re.match(r'^\((\d+)\)(.+?)\(([A-Z]{3})\)$', player_info)
                    if seeding_match:
                        seeding = int(seeding_match.group(1))
                        name = seeding_match.group(2).strip()
                        country = seeding_match.group(3)
                    else:
                        # No seeding
                        name_country_match = re.match(r'^(.+?)\(([A-Z]{3})\)$', player_info)
                        if name_country_match:
                            name = name_country_match.group(1).strip()
                            country = name_country_match.group(2)
                            seeding = None
                        else:
                            continue
                    
                    # Create advancement chances dictionary
                    advancement_chances = {
                        "R64": chances[0] if len(chances) > 0 else 0.0,
                        "R32": chances[1] if len(chances) > 1 else 0.0,
                        "R16": chances[2] if len(chances) > 2 else 0.0,
                        "QF": chances[3] if len(chances) > 3 else 0.0,
                        "SF": chances[4] if len(chances) > 4 else 0.0,
                        "F": chances[5] if len(chances) > 5 else 0.0,
                        "W": chances[6] if len(chances) > 6 else 0.0
                    }
                    
                    player = Player(
                        name=name,
                        country=country,
                        seeding=seeding,
                        advancement_chances=advancement_chances
                    )
                    players.append(player)
        
        return players
    
    def _create_draw(self, players: List[Player]) -> List[List[Player]]:
        """Create tournament draw structure (16 groups of 8 players each)"""
        # For now, we'll create a simple structure based on the data order
        # In a real implementation, you'd need to map the actual draw structure
        draw = []
        for i in range(0, len(players), 8):
            group = players[i:i+8]
            if len(group) == 8:
                draw.append(group)
        return draw
    
    def get_players_by_tier(self, gender: Gender) -> Dict[Tier, List[Player]]:
        """Categorize players into tiers based on their seeding"""
        players = self.men_players if gender == Gender.MEN else self.women_players
        
        # Sort players by seeding (None seeding goes to lowest tier)
        sorted_players = sorted(players, key=lambda p: (p.seeding is None, p.seeding or 999))
        
        # Divide into tiers (A: top 25%, B: next 25%, C: next 25%, D: bottom 25%)
        total_players = len(sorted_players)
        tier_size = total_players // 4
        
        tiers = {
            Tier.A: sorted_players[:tier_size],
            Tier.B: sorted_players[tier_size:2*tier_size],
            Tier.C: sorted_players[2*tier_size:3*tier_size],
            Tier.D: sorted_players[3*tier_size:]
        }
        
        return tiers
    
    def simulate_tournament(self, gender: Gender) -> List[Player]:
        """Simulate the entire tournament for the specified gender"""
        players = self.men_players if gender == Gender.MEN else self.women_players
        draw = self.men_draw if gender == Gender.MEN else self.women_draw
        
        # Reset all players
        for player in players:
            player.current_round = "R64"
            player.eliminated = False
        
        # Simulate each round
        rounds = ["R64", "R32", "R16", "QF", "SF", "F"]
        winners = []
        
        for round_name in rounds:
            if round_name == "R64":
                # First round - simulate within each group
                round_winners = []
                for group in draw:
                    # Simulate matches within the group (simplified - just take top 4)
                    group_winners = self._simulate_group_matches(group, round_name)
                    round_winners.extend(group_winners)
                winners = round_winners
            else:
                # Subsequent rounds - simulate matches between winners
                winners = self._simulate_round_matches(winners, round_name)
        
        return winners
    
    def _simulate_group_matches(self, group: List[Player], round_name: str) -> List[Player]:
        """Simulate matches within a group for the first round"""
        # Simplified simulation - just advance players based on their chances
        # In a real implementation, you'd need the actual draw structure
        group_winners = []
        
        # Simulate matches: 1v2, 3v4, 5v6, 7v8
        for i in range(0, len(group), 2):
            if i + 1 < len(group):
                match = Match(group[i], group[i+1])
                winner = match.simulate()
                group_winners.append(winner)
        
        return group_winners
    
    def _simulate_round_matches(self, players: List[Player], round_name: str) -> List[Player]:
        """Simulate matches for a specific round"""
        winners = []
        
        for i in range(0, len(players), 2):
            if i + 1 < len(players):
                match = Match(players[i], players[i+1])
                winner = match.simulate()
                winners.append(winner)
        
        return winners
    
    def simulate_scorito_game(self, selected_players: Dict[Gender, Dict[Tier, List[str]]]) -> Dict[str, int]:
        """Simulate a Scorito game with selected players"""
        results = {}
        
        for gender in Gender:
            gender_results = {}
            players = self.men_players if gender == Gender.MEN else self.women_players
            
            # Simulate tournament
            tournament_winners = self.simulate_tournament(gender)
            
            # Calculate points for selected players
            for tier in Tier:
                selected_names = selected_players[gender][tier]
                tier_points = 0
                
                for player_name in selected_names:
                    # Find the player in the tournament results
                    for player in players:
                        if player.get_clean_name() == player_name:
                            # Calculate points based on how far they advanced
                            points = self._calculate_scorito_points(player.current_round, player.eliminated)
                            tier_points += points
                            break
                
                gender_results[f"{tier.value}_tier"] = tier_points
            
            results[gender.value] = gender_results
        
        return results
    
    def _calculate_scorito_points(self, current_round: str, eliminated: bool) -> int:
        """Calculate Scorito points based on how far a player advanced"""
        if eliminated:
            return 0
        
        points_map = {
            "R64": 0,
            "R32": 1,
            "R16": 2,
            "QF": 4,
            "SF": 8,
            "F": 16,
            "W": 32
        }
        
        return points_map.get(current_round, 0)

def main():
    """Example usage of the tennis simulator"""
    # Initialize simulator
    simulator = TournamentSimulator("importdata_men.txt", "importdata_womens.txt")
    
    # Get players by tier
    men_tiers = simulator.get_players_by_tier(Gender.MEN)
    women_tiers = simulator.get_players_by_tier(Gender.WOMEN)
    
    print("=== MEN'S TOURNAMENT TIERS ===")
    for tier in Tier:
        print(f"\nTier {tier.value}:")
        for player in men_tiers[tier]:
            seeding_info = f"(#{player.seeding})" if player.seeding else "(unseeded)"
            print(f"  {player.get_clean_name()} {seeding_info} ({player.country})")
    
    print("\n=== WOMEN'S TOURNAMENT TIERS ===")
    for tier in Tier:
        print(f"\nTier {tier.value}:")
        for player in women_tiers[tier]:
            seeding_info = f"(#{player.seeding})" if player.seeding else "(unseeded)"
            print(f"  {player.get_clean_name()} {seeding_info} ({player.country})")
    
    # Example Scorito game simulation
    print("\n=== EXAMPLE SCORITO GAME SIMULATION ===")
    
    # Example selected players (you would replace this with actual selections)
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
    for gender, gender_results in results.items():
        print(f"\n{gender.upper()}:")
        total_points = 0
        for tier, points in gender_results.items():
            print(f"  {tier}: {points} points")
            total_points += points
        print(f"  Total: {total_points} points")

if __name__ == "__main__":
    main()
