#!/usr/bin/env python3
"""
Database-based Tennis Tournament Simulator for Scorito Game
This simulator uses the separate database files for men and women players.
"""

import random
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from men_database import MEN_PLAYERS, Tier as MenTier, MenPlayer
from women_database import WOMEN_PLAYERS, Tier as WomenTier, WomenPlayer

class Gender(Enum):
    MEN = "men"
    WOMEN = "women"

@dataclass
class Player:
    name: str
    country: str
    seeding: Optional[int]
    tier: str  # A, B, C, or D
    advancement_chances: Dict[str, float]  # R64, R32, R16, QF, SF, F, W
    current_round: str = "R64"
    eliminated: bool = False
    
    def get_advancement_chance(self, round_name: str) -> float:
        """Get the chance of advancing to the specified round"""
        return self.advancement_chances.get(round_name, 0.0)
    
    def get_clean_name(self) -> str:
        """Get player name without seeding information"""
        return self.name

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

class DatabaseTournamentSimulator:
    def __init__(self):
        self.men_players = self._convert_men_players()
        self.women_players = self._convert_women_players()
        self.men_draw = self._create_draw(self.men_players)
        self.women_draw = self._create_draw(self.women_players)
        
    def _convert_men_players(self) -> List[Player]:
        """Convert men database players to simulator format"""
        players = []
        for men_player in MEN_PLAYERS:
            advancement_chances = {
                "R64": men_player.r64_chance,
                "R32": men_player.r32_chance,
                "R16": men_player.r16_chance,
                "QF": men_player.qf_chance,
                "SF": men_player.sf_chance,
                "F": men_player.f_chance,
                "W": men_player.w_chance
            }
            
            player = Player(
                name=men_player.name,
                country=men_player.country,
                seeding=men_player.seeding,
                tier=men_player.tier.value,
                advancement_chances=advancement_chances
            )
            players.append(player)
        return players
    
    def _convert_women_players(self) -> List[Player]:
        """Convert women database players to simulator format"""
        players = []
        for women_player in WOMEN_PLAYERS:
            advancement_chances = {
                "R64": women_player.r64_chance,
                "R32": women_player.r32_chance,
                "R16": women_player.r16_chance,
                "QF": women_player.qf_chance,
                "SF": women_player.sf_chance,
                "F": women_player.f_chance,
                "W": women_player.w_chance
            }
            
            player = Player(
                name=women_player.name,
                country=women_player.country,
                seeding=women_player.seeding,
                tier=women_player.tier.value,
                advancement_chances=advancement_chances
            )
            players.append(player)
        return players
    
    def _create_draw(self, players: List[Player]) -> List[List[Player]]:
        """Create tournament draw structure (16 groups of 8 players each)"""
        draw = []
        for i in range(0, len(players), 8):
            group = players[i:i+8]
            if len(group) == 8:
                draw.append(group)
        return draw
    
    def get_players_by_tier(self, gender: Gender) -> Dict[str, List[Player]]:
        """Get players organized by tier using the database tier assignments"""
        players = self.men_players if gender == Gender.MEN else self.women_players
        
        tiers = {"A": [], "B": [], "C": [], "D": []}
        for player in players:
            tiers[player.tier].append(player)
        
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
                    group_winners = self._simulate_group_matches(group, round_name)
                    round_winners.extend(group_winners)
                winners = round_winners
            else:
                # Subsequent rounds - simulate matches between winners
                winners = self._simulate_round_matches(winners, round_name)
        
        return winners
    
    def _simulate_group_matches(self, group: List[Player], round_name: str) -> List[Player]:
        """Simulate matches within a group for the first round"""
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
    
    def simulate_scorito_game(self, selected_players: Dict[Gender, Dict[str, List[str]]]) -> Dict[str, int]:
        """Simulate a Scorito game with selected players"""
        results = {}
        
        for gender in Gender:
            gender_results = {}
            players = self.men_players if gender == Gender.MEN else self.women_players
            
            # Simulate tournament
            tournament_winners = self.simulate_tournament(gender)
            
            # Calculate points for selected players
            for tier in ["A", "B", "C", "D"]:
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
                
                gender_results[f"{tier}_tier"] = tier_points
            
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
    
    def get_player_recommendations(self, gender: Gender, num_simulations: int = 1000) -> Dict[str, List[Tuple[str, float]]]:
        """Get player recommendations for each tier based on simulation results"""
        players = self.men_players if gender == Gender.MEN else self.women_players
        tiers = self.get_players_by_tier(gender)
        
        # Run simulations to get player statistics
        player_stats = {}
        for player in players:
            player_stats[player.name] = {
                "rounds_reached": {"R64": 0, "R32": 0, "R16": 0, "QF": 0, "SF": 0, "F": 0, "W": 0}
            }
        
        for sim in range(num_simulations):
            tournament_results = self.simulate_tournament(gender)
            
            # Update player stats
            for round_name in ["R64", "R32", "R16", "QF", "SF", "F", "W"]:
                if round_name in tournament_results:
                    round_players = tournament_results[round_name]
                    for player in round_players:
                        if player.name in player_stats:
                            player_stats[player.name]["rounds_reached"][round_name] += 1
        
        # Calculate recommendations for each tier
        recommendations = {}
        
        for tier in ["A", "B", "C", "D"]:
            tier_players = tiers[tier]
            player_scores = []
            
            for player in tier_players:
                player_name = player.name
                stats = player_stats[player_name]
                
                # Calculate expected points
                expected_points = 0
                for round_name, count in stats["rounds_reached"].items():
                    points = self._calculate_scorito_points(round_name, False)
                    probability = count / num_simulations
                    expected_points += points * probability
                
                player_scores.append((player_name, expected_points))
            
            # Sort by expected points (descending)
            player_scores.sort(key=lambda x: x[1], reverse=True)
            recommendations[tier] = player_scores
        
        return recommendations

def main():
    """Example usage of the database-based simulator"""
    print("=== DATABASE-BASED TENNIS SIMULATOR ===")
    
    # Initialize simulator
    simulator = DatabaseTournamentSimulator()
    
    # Get players by tier
    men_tiers = simulator.get_players_by_tier(Gender.MEN)
    women_tiers = simulator.get_players_by_tier(Gender.WOMEN)
    
    print("\n=== MEN'S TOURNAMENT TIERS ===")
    for tier in ["A", "B", "C", "D"]:
        print(f"\nTier {tier}:")
        for player in men_tiers[tier]:
            seeding_info = f"(#{player.seeding})" if player.seeding else "(unseeded)"
            print(f"  {player.get_clean_name()} {seeding_info} ({player.country})")
    
    print("\n=== WOMEN'S TOURNAMENT TIERS ===")
    for tier in ["A", "B", "C", "D"]:
        print(f"\nTier {tier}:")
        for player in women_tiers[tier]:
            seeding_info = f"(#{player.seeding})" if player.seeding else "(unseeded)"
            print(f"  {player.get_clean_name()} {seeding_info} ({player.country})")
    
    # Get recommendations
    print("\n=== PLAYER RECOMMENDATIONS ===")
    
    for gender in Gender:
        print(f"\n{gender.value.upper()} TOURNAMENT RECOMMENDATIONS:")
        recommendations = simulator.get_player_recommendations(gender, num_simulations=500)
        
        for tier in ["A", "B", "C", "D"]:
            print(f"\nTier {tier} (Top 5):")
            for i, (player_name, expected_points) in enumerate(recommendations[tier][:5], 1):
                print(f"  {i}. {player_name}: {expected_points:.2f} expected points")
    
    # Example Scorito game simulation
    print("\n=== EXAMPLE SCORITO GAME SIMULATION ===")
    
    # Example selected players
    selected_players = {
        Gender.MEN: {
            "A": ["Jannik Sinner", "Carlos Alcaraz", "Novak Djokovic"],
            "B": ["Daniil Medvedev", "Alexander Zverev", "Taylor Fritz"],
            "C": ["Tommy Paul", "Frances Tiafoe", "Ben Shelton"],
            "D": ["Lorenzo Musetti", "Denis Shapovalov", "Grigor Dimitrov"]
        },
        Gender.WOMEN: {
            "A": ["Iga Swiatek", "Coco Gauff", "Aryna Sabalenka"],
            "B": ["Elena Rybakina", "Jessica Pegula", "Madison Keys"],
            "C": ["Paula Badosa", "Donna Vekic", "Elina Svitolina"],
            "D": ["Mirra Andreeva", "Emma Navarro", "Karolina Muchova"]
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

if __name__ == "__main__":
    main()
