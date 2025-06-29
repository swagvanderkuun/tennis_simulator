"""
Tournament simulator using fixed draws from import data files.
"""

import random
from typing import List, Dict, Optional, Tuple
from collections import defaultdict, Counter
import statistics
from tqdm import tqdm
import re

from ..core.models import (
    Player, Match, Tournament, Round, Gender, Tier, ScoritoGame
)
from ..data.player_database import player_db


class ImportDataParser:
    """Parser for import data files containing fixed tournament draws."""
    
    def __init__(self):
        self.men_draw_data = {}
        self.women_draw_data = {}
    
    def parse_import_file(self, filepath: str) -> Dict[str, Dict[str, float]]:
        """Parse import data file and extract player advancement probabilities."""
        draw_data = {}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            print(f"Parsing {filepath} with {len(lines)} lines")
            current_section = []
            section_count = 0
            for line_num, line in enumerate(lines):
                line_stripped = line.strip()
                # Only skip header lines
                if line_stripped.startswith('2025') or line_stripped.startswith('Player'):
                    continue
                # Section separator: any line that is empty after strip
                if line_stripped == '':
                    if current_section:
                        section_count += 1
                        print(f"Processing section {section_count} with {len(current_section)} lines")
                        self._process_section(current_section, draw_data)
                        current_section = []
                    continue
                current_section.append(line_stripped)
            # Process the last section
            if current_section:
                section_count += 1
                print(f"Processing final section {section_count} with {len(current_section)} lines")
                self._process_section(current_section, draw_data)
            print(f"Parsed {len(draw_data)} players from {filepath}")
            return draw_data
        except Exception as e:
            print(f"Error parsing import file {filepath}: {e}")
            return {}
    
    def _process_section(self, section_lines: List[str], draw_data: Dict[str, Dict[str, float]]):
        """Process a section of the draw (8 players forming 4 matches)."""
        if len(section_lines) != 8:
            print(f"Section has {len(section_lines)} lines, expected 8")
            return
        
        # Extract player names and probabilities
        for line in section_lines:
            # Split by tabs and filter out empty strings
            parts = [part.strip() for part in line.split('\t') if part.strip()]
            
            print(f"Processing line: '{line}' -> {len(parts)} parts: {parts}")
            
            if len(parts) >= 8:  # Player name + 7 probability columns
                player_name = parts[0]
                # Clean player name (remove seeding)
                clean_name = self._clean_player_name(player_name)
                
                # Extract probabilities for each round
                probabilities = {}
                try:
                    probabilities['R64'] = float(parts[1].replace('%', '')) / 100
                    probabilities['R32'] = float(parts[2].replace('%', '')) / 100
                    probabilities['R16'] = float(parts[3].replace('%', '')) / 100
                    probabilities['QF'] = float(parts[4].replace('%', '')) / 100
                    probabilities['SF'] = float(parts[5].replace('%', '')) / 100
                    probabilities['F'] = float(parts[6].replace('%', '')) / 100
                    probabilities['W'] = float(parts[7].replace('%', '')) / 100
                    
                    draw_data[clean_name] = probabilities
                    print(f"Added player: {clean_name}")
                except (ValueError, IndexError) as e:
                    print(f"Error parsing line '{line}': {e}")
                    continue
            else:
                print(f"Line has insufficient parts: {len(parts)} < 8")
    
    def _clean_player_name(self, player_name: str) -> str:
        """Clean player name by removing seeding information and country codes."""
        # Remove seeding like "(1)", "(2)", etc. at the beginning
        name = re.sub(r"^\(\d+\)", "", player_name.strip())
        
        # Remove country codes like "(ITA)", "(USA)", etc. at the end
        name = re.sub(r"\([A-Z]{3}\)\s*$", "", name.strip())
        
        return name.strip()
    
    def load_draw_data(self, men_file: str, women_file: str):
        """Load draw data from both men's and women's import files."""
        self.men_draw_data = self.parse_import_file(men_file)
        self.women_draw_data = self.parse_import_file(women_file)
        
        print(f"Loaded {len(self.men_draw_data)} men's players and {len(self.women_draw_data)} women's players")


class FixedDrawSimulator:
    """Simulator that uses fixed tournament draws from import data."""
    
    def __init__(self, tournament_name: str = "Wimbledon"):
        self.tournament_name = tournament_name
        self.men_tournament: Optional[Tournament] = None
        self.women_tournament: Optional[Tournament] = None
        self.simulation_results: List[Dict] = []
        self.parser = ImportDataParser()
        
        # Load draw data
        self.parser.load_draw_data(
            "data/elo/importdata_men.txt",
            "data/elo/importdata_women.txt"
        )
    
    def setup_tournaments(self, men_players: List[Player], women_players: List[Player]):
        """Setup tournaments with fixed draws from import data."""
        # Load import data
        self.parser.load_draw_data(
            "data/elo/importdata_men.txt",
            "data/elo/importdata_women.txt"
        )
        
        # Create complete player lists from import data
        men_draw_players = self._create_players_from_import_data(self.parser.men_draw_data, Gender.MEN)
        women_draw_players = self._create_players_from_import_data(self.parser.women_draw_data, Gender.WOMEN)
        
        # Create fixed draws based on import data order
        men_draw = self._create_fixed_draw(men_draw_players, self.parser.men_draw_data)
        women_draw = self._create_fixed_draw(women_draw_players, self.parser.women_draw_data)
        
        # Create tournaments with fixed draws
        self.men_tournament = Tournament(
            name=f"{self.tournament_name} Men's",
            players=men_draw,
            gender=Gender.MEN
        )
        
        self.women_tournament = Tournament(
            name=f"{self.tournament_name} Women's", 
            players=women_draw,
            gender=Gender.WOMEN
        )
    
    def _create_players_from_import_data(self, draw_data: dict, gender: Gender) -> list:
        """Create Player objects for all players in the import data, extracting name, country, seeding, and setting tier."""
        players = []
        for player_name in draw_data.keys():
            # Extract seeding if present (e.g., (1)Name)
            seeding_match = re.match(r"\((\d+)\)", player_name.strip())
            seeding = int(seeding_match.group(1)) if seeding_match else None
            # Extract country (last (XXX))
            country_match = re.search(r"\(([A-Z]{3})\)\s*$", player_name)
            country = country_match.group(1) if country_match else "UNK"
            # Clean name: remove seeding and country
            name = re.sub(r"^\(\d+\)", "", player_name).strip()
            name = re.sub(r"\([A-Z]{3}\)\s*$", "", name).strip()
            # Create player
            players.append(Player(
                name=name,
                country=country,
                seeding=seeding,
                tier=Tier.D
            ))
        return players
    
    def simulate_player_advancement(self, player_name: str, current_round: Round, draw_data: Dict[str, Dict[str, float]]) -> bool:
        """Simulate if a player advances to the next round based on import data probabilities."""
        if player_name not in draw_data:
            # If player not in import data, use 50/50 chance
            return random.random() < 0.5
        
        player_probs = draw_data[player_name]
        
        # Get probability for current round
        round_key = current_round.value
        if round_key not in player_probs:
            return random.random() < 0.5
        
        # Get probability for next round
        next_round_key = self._get_next_round_key(round_key)
        if next_round_key not in player_probs:
            return random.random() < 0.5
        
        current_prob = player_probs[round_key]
        next_prob = player_probs[next_round_key]
        
        # Calculate advancement probability
        if current_prob > 0:
            advancement_prob = next_prob / current_prob
        else:
            advancement_prob = 0
        
        return random.random() < advancement_prob
    
    def _get_next_round_key(self, current_round: str) -> str:
        """Get the next round key."""
        round_progression = {
            'R64': 'R32',
            'R32': 'R16',
            'R16': 'QF',
            'QF': 'SF',
            'SF': 'F',
            'F': 'W'
        }
        return round_progression.get(current_round, 'W')
    
    def simulate_tournament(self, tournament: Tournament, draw_data: Dict[str, Dict[str, float]]) -> Player:
        """Simulate a complete tournament using fixed draw data."""
        tournament.reset()
        
        # Get all players in the tournament
        players = tournament.players.copy()
        
        # Simulate each round
        rounds = [Round.R64, Round.R32, Round.R16, Round.QF, Round.SF, Round.F]
        current_players = players.copy()
        
        for round_type in rounds:
            if len(current_players) <= 1:
                break
            
            # Simulate matches in this round
            next_round_players = []
            
            # Process players in pairs (matches)
            for i in range(0, len(current_players), 2):
                if i + 1 < len(current_players):
                    player1 = current_players[i]
                    player2 = current_players[i + 1]
                    
                    # Create match
                    match = Match(player1, player2, round_type)
                    tournament.matches.append(match)
                    
                    # Simulate match outcome
                    if self.simulate_player_advancement(player1.name, round_type, draw_data):
                        winner = player1
                        loser = player2
                    else:
                        winner = player2
                        loser = player1
                    
                    # Update match result
                    match.winner = winner
                    match.loser = loser
                    
                    # Update player states
                    loser.eliminated = True
                    winner.current_round = self._get_next_round(round_type)
                    
                    next_round_players.append(winner)
            
            current_players = next_round_players
        
        # Set winner
        if current_players:
            tournament.winner = current_players[0]
            tournament.completed = True
        
        return tournament.winner
    
    def _get_next_round(self, current_round: Round) -> Round:
        """Get the next round after current match round."""
        round_progression = {
            Round.R64: Round.R32,
            Round.R32: Round.R16,
            Round.R16: Round.QF,
            Round.QF: Round.SF,
            Round.SF: Round.F,
            Round.F: Round.W
        }
        return round_progression.get(current_round, Round.W)
    
    def run_single_simulation(self) -> Dict:
        """Run a single simulation of both tournaments."""
        if not self.men_tournament or not self.women_tournament:
            raise ValueError("Tournaments not set up. Call setup_tournaments() first.")
        
        # Simulate men's tournament
        men_winner = self.simulate_tournament(self.men_tournament, self.parser.men_draw_data)
        
        # Simulate women's tournament
        women_winner = self.simulate_tournament(self.women_tournament, self.parser.women_draw_data)
        
        # Collect results
        result = {
            "men_winner": men_winner.name if men_winner else None,
            "women_winner": women_winner.name if women_winner else None,
            "men_finalists": [p.name for p in self.men_tournament.get_players_in_round(Round.F)],
            "women_finalists": [p.name for p in self.women_tournament.get_players_in_round(Round.F)],
            "men_semifinalists": [p.name for p in self.men_tournament.get_players_in_round(Round.SF)],
            "women_semifinalists": [p.name for p in self.women_tournament.get_players_in_round(Round.SF)],
            "men_quarterfinalists": [p.name for p in self.men_tournament.get_players_in_round(Round.QF)],
            "women_quarterfinalists": [p.name for p in self.women_tournament.get_players_in_round(Round.QF)]
        }
        
        return result
    
    def run_multiple_simulations(self, num_simulations: int = 1000) -> Dict:
        """Run multiple simulations and collect statistics."""
        print(f"Running {num_simulations} simulations using fixed draw data...")
        
        all_results = []
        men_winners = Counter()
        women_winners = Counter()
        men_finalists = Counter()
        women_finalists = Counter()
        men_semifinalists = Counter()
        women_semifinalists = Counter()
        
        for _ in tqdm(range(num_simulations), desc="Simulating tournaments"):
            result = self.run_single_simulation()
            all_results.append(result)
            
            # Count winners
            if result["men_winner"]:
                men_winners[result["men_winner"]] += 1
            if result["women_winner"]:
                women_winners[result["women_winner"]] += 1
            
            # Count finalists
            for player in result["men_finalists"]:
                men_finalists[player] += 1
            for player in result["women_finalists"]:
                women_finalists[player] += 1
            
            # Count semifinalists
            for player in result["men_semifinalists"]:
                men_semifinalists[player] += 1
            for player in result["women_semifinalists"]:
                women_semifinalists[player] += 1
        
        # Calculate statistics
        stats = {
            "total_simulations": num_simulations,
            "men_win_probabilities": {name: count/num_simulations for name, count in men_winners.most_common(10)},
            "women_win_probabilities": {name: count/num_simulations for name, count in women_winners.most_common(10)},
            "men_final_probabilities": {name: count/num_simulations for name, count in men_finalists.most_common(10)},
            "women_final_probabilities": {name: count/num_simulations for name, count in women_finalists.most_common(10)},
            "men_semifinal_probabilities": {name: count/num_simulations for name, count in men_semifinalists.most_common(10)},
            "women_semifinal_probabilities": {name: count/num_simulations for name, count in women_semifinalists.most_common(10)}
        }
        
        self.simulation_results = all_results
        return stats
    
    def get_player_recommendations(self, gender: Gender, tier: Tier, num_recommendations: int = 5) -> List[Tuple[Player, Dict]]:
        """Get player recommendations for a specific tier based on simulation results."""
        if not self.simulation_results:
            raise ValueError("No simulation results available. Run simulations first.")
        
        players = player_db.get_players_by_tier(gender, tier)
        recommendations = []
        
        # New tier-based scoring system
        tier_scoring = {
            Tier.A: [10, 20, 30, 40, 60, 80, 100],  # R64, R32, R16, QF, SF, F, W
            Tier.B: [20, 40, 60, 80, 100, 120, 140],
            Tier.C: [30, 60, 90, 120, 140, 160, 180],
            Tier.D: [60, 90, 120, 160, 180, 200, 200]
        }
        
        round_to_index = {
            Round.R64: 0,  # Round 1
            Round.R32: 1,  # Round 2
            Round.R16: 2,  # Round 3
            Round.QF: 3,   # Round 4
            Round.SF: 4,   # Round 5
            Round.F: 5,    # Round 6
            Round.W: 6     # Round 7
        }
        
        scoring = tier_scoring.get(tier, tier_scoring[Tier.D])
        
        for player in players:
            # Count how often this player reaches different rounds
            round_counts = {round_type: 0 for round_type in Round}
            
            for result in self.simulation_results:
                if gender == Gender.MEN:
                    if result["men_winner"] == player.name:
                        round_counts[Round.W] += 1
                    elif player.name in result["men_finalists"]:
                        round_counts[Round.F] += 1
                    elif player.name in result["men_semifinalists"]:
                        round_counts[Round.SF] += 1
                    elif player.name in result["men_quarterfinalists"]:
                        round_counts[Round.QF] += 1
                    else:
                        # Check if player was eliminated in earlier rounds
                        for match in result.get("men_matches", []):
                            if match.get("loser") == player.name:
                                # Find the round where they lost
                                if match.get("round") == "R64":
                                    round_counts[Round.R64] += 1
                                elif match.get("round") == "R32":
                                    round_counts[Round.R32] += 1
                                elif match.get("round") == "R16":
                                    round_counts[Round.R16] += 1
                                break
                else:
                    if result["women_winner"] == player.name:
                        round_counts[Round.W] += 1
                    elif player.name in result["women_finalists"]:
                        round_counts[Round.F] += 1
                    elif player.name in result["women_semifinalists"]:
                        round_counts[Round.SF] += 1
                    elif player.name in result["women_quarterfinalists"]:
                        round_counts[Round.QF] += 1
                    else:
                        # Check if player was eliminated in earlier rounds
                        for match in result.get("women_matches", []):
                            if match.get("loser") == player.name:
                                # Find the round where they lost
                                if match.get("round") == "R64":
                                    round_counts[Round.R64] += 1
                                elif match.get("round") == "R32":
                                    round_counts[Round.R32] += 1
                                elif match.get("round") == "R16":
                                    round_counts[Round.R16] += 1
                                break
            
            total_sims = len(self.simulation_results)
            
            # Calculate expected points using new scoring system
            expected_points = 0
            for round_type, count in round_counts.items():
                round_index = round_to_index.get(round_type, 0)
                if round_index < len(scoring):
                    expected_points += (count * scoring[round_index]) / total_sims
            
            stats = {
                "win_rate": round_counts[Round.W] / total_sims * 100,
                "final_rate": round_counts[Round.F] / total_sims * 100,
                "semifinal_rate": round_counts[Round.SF] / total_sims * 100,
                "quarterfinal_rate": round_counts[Round.QF] / total_sims * 100,
                "expected_points": expected_points
            }
            
            recommendations.append((player, stats))
        
        # Sort by expected points
        recommendations.sort(key=lambda x: x[1]["expected_points"], reverse=True)
        
        return recommendations[:num_recommendations]
    
    def simulate_scorito_game(self, game: ScoritoGame) -> Dict:
        """Simulate a Scorito game with the given player selections."""
        if not self.men_tournament or not self.women_tournament:
            raise ValueError("Tournaments not set up. Call setup_tournaments() first.")
        
        # Run simulation
        result = self.run_single_simulation()
        
        # Calculate points
        points = game.calculate_points()
        
        return {
            "simulation_result": result,
            "scorito_points": points,
            "total_points": game.total_points
        }
    
    def print_simulation_summary(self, stats: Dict) -> None:
        """Print a summary of simulation results."""
        print(f"\n{'='*60}")
        print(f"SIMULATION SUMMARY ({stats['total_simulations']} simulations)")
        print(f"Using fixed draw data from import files")
        print(f"{'='*60}")
        
        print(f"\nMEN'S TOURNAMENT - WIN PROBABILITIES:")
        print("-" * 40)
        for player, prob in stats["men_win_probabilities"].items():
            print(f"{player:25} {prob*100:5.1f}%")
        
        print(f"\nWOMEN'S TOURNAMENT - WIN PROBABILITIES:")
        print("-" * 40)
        for player, prob in stats["women_win_probabilities"].items():
            print(f"{player:25} {prob*100:5.1f}%")
        
        print(f"\nMEN'S TOURNAMENT - FINAL PROBABILITIES:")
        print("-" * 40)
        for player, prob in stats["men_final_probabilities"].items():
            print(f"{player:25} {prob*100:5.1f}%")
        
        print(f"\nWOMEN'S TOURNAMENT - FINAL PROBABILITIES:")
        print("-" * 40)
        for player, prob in stats["women_final_probabilities"].items():
            print(f"{player:25} {prob*100:5.1f}%")

    def _create_fixed_draw(self, players: List[Player], draw_data: Dict[str, Dict[str, float]]) -> List[Player]:
        """Create a fixed draw based on the import data file order."""
        # Sort players by their order in the import data file
        ordered_players = []
        
        # Get all player names from draw_data in order
        for player_name, probabilities in draw_data.items():
            # Clean the player name (same logic as parser)
            cleaned_name = self.parser._clean_player_name(player_name)
            
            # Find the corresponding player in our database
            for player in players:
                if player.name == cleaned_name:
                    ordered_players.append(player)
                    break
        
        # If we couldn't find all players, add the remaining ones at the end
        found_names = {p.name for p in ordered_players}
        for player in players:
            if player.name not in found_names:
                ordered_players.append(player)
        
        return ordered_players


# Convenience function to create and run simulations
def run_tournament_simulation(
    num_simulations: int = 1000,
    tournament_name: str = "Wimbledon",
    use_elo: bool = True
) -> FixedDrawSimulator:
    """Convenience function to run tournament simulations with fixed draws."""
    
    # Get all players
    men_players = list(player_db.get_players_by_gender(Gender.MEN).values())
    women_players = list(player_db.get_players_by_gender(Gender.WOMEN).values())
    
    # Create simulator
    simulator = FixedDrawSimulator(tournament_name)
    simulator.setup_tournaments(men_players, women_players)
    
    # Run simulations
    stats = simulator.run_multiple_simulations(num_simulations)
    
    # Print summary
    simulator.print_simulation_summary(stats)
    
    return simulator 