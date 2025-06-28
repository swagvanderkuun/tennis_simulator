#!/usr/bin/env python3
"""
Advanced Tennis Tournament Simulator for Scorito Game
This version provides more realistic tournament simulation with proper draw structure.
"""

import random
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from tennis_simulator import TournamentSimulator, Gender, Tier, Player, Match

class AdvancedTournamentSimulator(TournamentSimulator):
    def __init__(self, men_data_file: str, women_data_file: str):
        super().__init__(men_data_file, women_data_file)
        self.men_draw_structure = self._create_proper_draw_structure(self.men_players)
        self.women_draw_structure = self._create_proper_draw_structure(self.women_players)
    
    def _create_proper_draw_structure(self, players: List[Player]) -> Dict[str, List[Player]]:
        """Create a proper tournament draw structure based on seeding"""
        # Sort players by seeding
        seeded_players = [p for p in players if p.seeding is not None]
        unseeded_players = [p for p in players if p.seeding is None]
        
        # Sort seeded players by seeding
        seeded_players.sort(key=lambda p: p.seeding)
        
        # Create draw structure (128 players total, 16 sections of 8 players each)
        draw_structure = {}
        
        # For simplicity, we'll create a basic structure
        # In a real Grand Slam, the draw is more complex with specific seeding placement
        for i in range(16):
            section_name = f"Section_{i+1}"
            section_players = []
            
            # Add seeded players first (if available)
            if i < len(seeded_players):
                section_players.append(seeded_players[i])
            
            # Fill remaining spots with unseeded players
            while len(section_players) < 8 and unseeded_players:
                section_players.append(unseeded_players.pop(0))
            
            draw_structure[section_name] = section_players
        
        return draw_structure
    
    def simulate_tournament_advanced(self, gender: Gender) -> Dict[str, List[Player]]:
        """Simulate tournament with proper draw structure"""
        players = self.men_players if gender == Gender.MEN else self.women_players
        draw_structure = self.men_draw_structure if gender == Gender.MEN else self.women_draw_structure
        
        # Reset all players
        for player in players:
            player.current_round = "R64"
            player.eliminated = False
        
        # Simulate each round
        rounds = ["R64", "R32", "R16", "QF", "SF", "F"]
        round_results = {}
        
        current_players = players.copy()
        
        for round_name in rounds:
            if round_name == "R64":
                # First round - simulate within each section
                round_winners = []
                for section_name, section_players in draw_structure.items():
                    section_winners = self._simulate_section_matches(section_players, round_name)
                    round_winners.extend(section_winners)
                current_players = round_winners
            else:
                # Subsequent rounds - simulate matches between winners
                current_players = self._simulate_round_matches_advanced(current_players, round_name)
            
            round_results[round_name] = current_players.copy()
        
        return round_results
    
    def _simulate_section_matches(self, section_players: List[Player], round_name: str) -> List[Player]:
        """Simulate matches within a section for the first round"""
        if len(section_players) < 2:
            return section_players
        
        # Create matches: 1v8, 2v7, 3v6, 4v5 (typical Grand Slam draw)
        matches = []
        for i in range(len(section_players) // 2):
            player1 = section_players[i]
            player2 = section_players[-(i+1)]
            matches.append(Match(player1, player2))
        
        # Simulate all matches
        winners = []
        for match in matches:
            winner = match.simulate()
            winners.append(winner)
        
        return winners
    
    def _simulate_round_matches_advanced(self, players: List[Player], round_name: str) -> List[Player]:
        """Simulate matches for a specific round with proper pairing"""
        if len(players) < 2:
            return players
        
        winners = []
        
        # Create matches based on typical tournament structure
        # In a real tournament, this would follow the draw bracket
        for i in range(0, len(players), 2):
            if i + 1 < len(players):
                match = Match(players[i], players[i+1])
                winner = match.simulate()
                winners.append(winner)
        
        return winners
    
    def simulate_multiple_tournaments(self, gender: Gender, num_simulations: int = 1000) -> Dict[str, Dict]:
        """Run multiple tournament simulations to get statistical results"""
        results = {
            "player_stats": {},
            "tier_stats": {},
            "round_stats": {}
        }
        
        # Initialize player stats
        players = self.men_players if gender == Gender.MEN else self.women_players
        for player in players:
            results["player_stats"][player.get_clean_name()] = {
                "wins": 0,
                "rounds_reached": {"R64": 0, "R32": 0, "R16": 0, "QF": 0, "SF": 0, "F": 0, "W": 0}
            }
        
        # Initialize tier stats
        tiers = self.get_players_by_tier(gender)
        for tier in Tier:
            results["tier_stats"][tier.value] = {
                "total_points": 0,
                "avg_points": 0,
                "best_performance": 0
            }
        
        # Run simulations
        for sim in range(num_simulations):
            tournament_results = self.simulate_tournament_advanced(gender)
            
            # Update player stats
            for round_name, round_players in tournament_results.items():
                for player in round_players:
                    player_name = player.get_clean_name()
                    if player_name in results["player_stats"]:
                        results["player_stats"][player_name]["rounds_reached"][round_name] += 1
                        if round_name == "W":
                            results["player_stats"][player_name]["wins"] += 1
            
            # Calculate tier performance for this simulation
            tier_points = self._calculate_tier_performance(tournament_results, tiers)
            for tier, points in tier_points.items():
                results["tier_stats"][tier]["total_points"] += points
                results["tier_stats"][tier]["best_performance"] = max(
                    results["tier_stats"][tier]["best_performance"], points
                )
        
        # Calculate averages
        for tier in Tier:
            results["tier_stats"][tier.value]["avg_points"] = (
                results["tier_stats"][tier.value]["total_points"] / num_simulations
            )
        
        return results
    
    def _calculate_tier_performance(self, tournament_results: Dict[str, List[Player]], 
                                  tiers: Dict[Tier, List[Player]]) -> Dict[str, int]:
        """Calculate tier performance for a single tournament simulation"""
        tier_points = {tier.value: 0 for tier in Tier}
        
        # Calculate points for each tier
        for tier, tier_players in tiers.items():
            for player in tier_players:
                # Find the highest round this player reached
                highest_round = "R64"
                for round_name in ["R32", "R16", "QF", "SF", "F", "W"]:
                    if round_name in tournament_results:
                        round_players = tournament_results[round_name]
                        if any(p.get_clean_name() == player.get_clean_name() for p in round_players):
                            highest_round = round_name
                
                # Calculate points
                points = self._calculate_scorito_points(highest_round, False)
                tier_points[tier.value] += points
        
        return tier_points
    
    def get_player_recommendations(self, gender: Gender, num_simulations: int = 1000) -> Dict[Tier, List[Tuple[str, float]]]:
        """Get player recommendations for each tier based on simulation results"""
        simulation_results = self.simulate_multiple_tournaments(gender, num_simulations)
        tiers = self.get_players_by_tier(gender)
        
        recommendations = {}
        
        for tier in Tier:
            tier_players = tiers[tier]
            player_scores = []
            
            for player in tier_players:
                player_name = player.get_clean_name()
                player_stats = simulation_results["player_stats"][player_name]
                
                # Calculate expected points
                expected_points = 0
                for round_name, count in player_stats["rounds_reached"].items():
                    points = self._calculate_scorito_points(round_name, False)
                    probability = count / num_simulations
                    expected_points += points * probability
                
                player_scores.append((player_name, expected_points))
            
            # Sort by expected points (descending)
            player_scores.sort(key=lambda x: x[1], reverse=True)
            recommendations[tier] = player_scores
        
        return recommendations

def main():
    """Example usage of the advanced simulator"""
    print("=== ADVANCED TENNIS TOURNAMENT SIMULATOR ===")
    
    # Initialize advanced simulator
    simulator = AdvancedTournamentSimulator("importdata_men.txt", "importdata_womens.txt")
    
    # Get player recommendations
    print("\n=== PLAYER RECOMMENDATIONS ===")
    
    for gender in Gender:
        print(f"\n{gender.value.upper()} TOURNAMENT RECOMMENDATIONS:")
        recommendations = simulator.get_player_recommendations(gender, num_simulations=1000)
        
        for tier in Tier:
            print(f"\nTier {tier.value} (Top 5 recommendations):")
            for i, (player_name, expected_points) in enumerate(recommendations[tier][:5], 1):
                print(f"  {i}. {player_name}: {expected_points:.2f} expected points")
    
    # Run statistical analysis
    print("\n=== STATISTICAL ANALYSIS ===")
    
    for gender in Gender:
        print(f"\n{gender.value.upper()} TOURNAMENT STATISTICS:")
        stats = simulator.simulate_multiple_tournaments(gender, num_simulations=1000)
        
        print("\nTier Performance (average points per simulation):")
        for tier, tier_stats in stats["tier_stats"].items():
            print(f"  Tier {tier}: {tier_stats['avg_points']:.2f} avg points, "
                  f"{tier_stats['best_performance']} best performance")
        
        print("\nTop 10 Most Successful Players:")
        player_success = []
        for player_name, player_stats in stats["player_stats"].items():
            total_rounds = sum(player_stats["rounds_reached"].values())
            if total_rounds > 0:  # Only include players who advanced at least once
                player_success.append((player_name, total_rounds, player_stats["wins"]))
        
        player_success.sort(key=lambda x: x[1], reverse=True)
        for i, (player_name, total_rounds, wins) in enumerate(player_success[:10], 1):
            print(f"  {i}. {player_name}: {total_rounds} total advances, {wins} wins")

if __name__ == "__main__":
    main()
