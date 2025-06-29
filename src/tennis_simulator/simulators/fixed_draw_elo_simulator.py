"""
Fixed Draw Elo Simulator - Uses fixed tournament draws from import data with Elo-based match simulation.
"""

import re
from typing import List, Dict, Optional, Tuple
from collections import defaultdict, Counter
import statistics
from tqdm import tqdm

from ..core.models import (
    Player, Match, Tournament, Round, Gender, Tier, ScoritoGame
)
from ..data.static_database import populate_static_database
from .elo_match_simulator import EloMatchSimulator, EloWeights, create_match_simulator


class FixedDrawParser:
    """Parser for import data files to extract fixed tournament draw structure."""
    
    def __init__(self):
        self.men_draw_structure = []
        self.women_draw_structure = []
    
    def parse_import_file(self, filepath: str) -> List[List[str]]:
        """Parse import data file and extract draw structure (groups of 8 players)."""
        draw_structure = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            current_section = []
            for line in lines:
                line_stripped = line.strip()
                # Skip header lines
                if line_stripped.startswith('2025') or line_stripped.startswith('Player'):
                    continue
                # Section separator: empty line
                if line_stripped == '':
                    if current_section:
                        # Extract player names from this section
                        section_players = self._extract_players_from_section(current_section)
                        if section_players:
                            draw_structure.append(section_players)
                        current_section = []
                    continue
                current_section.append(line_stripped)
            
            # Process the last section
            if current_section:
                section_players = self._extract_players_from_section(current_section)
                if section_players:
                    draw_structure.append(section_players)
            
            print(f"Parsed {len(draw_structure)} sections from {filepath}")
            return draw_structure
            
        except Exception as e:
            print(f"Error parsing import file {filepath}: {e}")
            return []
    
    def _extract_players_from_section(self, section_lines: List[str]) -> List[str]:
        """Extract player names from a section (8 lines)."""
        players = []
        for line in section_lines:
            # Split by tabs and get the first part (player name)
            parts = [part.strip() for part in line.split('\t') if part.strip()]
            if parts:
                player_name = parts[0]
                # Clean player name (remove seeding and country)
                clean_name = self._clean_player_name(player_name)
                players.append(clean_name)
        return players
    
    def _clean_player_name(self, player_name: str) -> str:
        """Clean player name by removing seeding information and country codes."""
        # Remove seeding like "(1)", "(2)", etc. at the beginning
        name = re.sub(r"^\(\d+\)", "", player_name.strip())
        
        # Remove country codes like "(ITA)", "(USA)", etc. at the end
        name = re.sub(r"\([A-Z]{3}\)\s*$", "", name.strip())
        
        return name.strip()
    
    def load_draw_data(self, men_file: str, women_file: str):
        """Load draw structure from both men's and women's import files."""
        self.men_draw_structure = self.parse_import_file(men_file)
        self.women_draw_structure = self.parse_import_file(women_file)
        
        print(f"Loaded {len(self.men_draw_structure)} men's sections and {len(self.women_draw_structure)} women's sections")


class FixedDrawEloSimulator:
    """
    Tournament simulator that uses fixed tournament draws from import data 
    and simulates matches using Elo-based match simulation.
    """
    
    def __init__(self, tournament_name: str = "Wimbledon", surface: str = "grass"):
        self.tournament_name = tournament_name
        self.surface = surface
        self.men_tournament: Optional[Tournament] = None
        self.women_tournament: Optional[Tournament] = None
        self.simulation_results: List[Dict] = []
        self.match_simulator = create_match_simulator(surface=surface)
        self.parser = FixedDrawParser()
        
        # Load static databases
        self.men_db = populate_static_database('men')
        self.women_db = populate_static_database('women')
        
        # Load draw data
        self.parser.load_draw_data(
            "data/elo/importdata_men.txt",
            "data/elo/importdata_women.txt"
        )
    
    def setup_tournaments(self):
        """Setup tournaments with fixed draws from import data."""
        # Create complete player lists from import data
        men_draw_players = self._create_players_from_draw_structure(self.parser.men_draw_structure, Gender.MEN)
        women_draw_players = self._create_players_from_draw_structure(self.parser.women_draw_structure, Gender.WOMEN)
        
        # Create fixed draws based on import data order
        men_draw = self._create_fixed_draw(men_draw_players, self.parser.men_draw_structure)
        women_draw = self._create_fixed_draw(women_draw_players, self.parser.women_draw_structure)
        
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
    
    def _create_players_from_draw_structure(self, draw_structure: List[List[str]], gender: Gender) -> List[Player]:
        """Create Player objects for all players in the draw structure."""
        players = []
        db = self.men_db if gender == Gender.MEN else self.women_db
        
        # Flatten the draw structure to get all player names
        all_player_names = []
        for section in draw_structure:
            all_player_names.extend(section)
        
        # Create Player objects, matching with static database
        for player_name in all_player_names:
            # Try to find player in static database
            player_data = db.get(player_name)
            
            if player_data:
                # Create player with data from static database
                player = Player(
                    name=player_name,
                    country="N/A",  # Static DB doesn't have country
                    seeding=None,  # Will be set later if needed
                    tier=Tier(player_data.tier),
                    elo=player_data.elo,
                    helo=player_data.helo,
                    celo=player_data.celo,
                    gelo=player_data.gelo,
                    yelo=player_data.yelo,
                    atp_rank=player_data.ranking if hasattr(player_data, 'ranking') else None,
                    wta_rank=player_data.ranking if hasattr(player_data, 'ranking') else None
                )
            else:
                # Create player with minimal data if not found in database
                player = Player(
                    name=player_name,
                    country="UNK",
                    seeding=None,
                    tier=Tier.D,
                    elo=1500,  # Default Elo
                    helo=1500,
                    celo=1500,
                    gelo=1500,
                    yelo=1500
                )
            
            players.append(player)
        
        return players
    
    def _create_fixed_draw(self, players: List[Player], draw_structure: List[List[str]]) -> List[Player]:
        """Create a fixed draw based on the import data file structure."""
        # Create a mapping from player names to Player objects
        player_map = {player.name: player for player in players}
        
        # Build the draw in the order specified by the import data
        ordered_players = []
        
        for section in draw_structure:
            for player_name in section:
                if player_name in player_map:
                    ordered_players.append(player_map[player_name])
        
        return ordered_players
    
    def simulate_tournament(self, tournament: Tournament) -> Player:
        """Simulate a complete tournament using Elo-based match simulation."""
        if not tournament.players:
            raise ValueError("Tournament has no players")
        
        # Reset tournament state
        tournament.reset()
        
        # Simulate tournament rounds
        current_players = tournament.players.copy()
        
        while len(current_players) > 1:
            # Determine current round based on number of players
            if len(current_players) == 2:
                round_name = Round.F
            elif len(current_players) == 4:
                round_name = Round.SF
            elif len(current_players) == 8:
                round_name = Round.QF
            elif len(current_players) == 16:
                round_name = Round.R4
            elif len(current_players) == 32:
                round_name = Round.R3
            elif len(current_players) == 64:
                round_name = Round.R2
            elif len(current_players) == 128:
                round_name = Round.R1
            else:
                round_name = Round.R1
            matches = self._create_matches_for_round(current_players, round_name)
            winners = []
            for match in matches:
                winner, loser, details = self.match_simulator.simulate_match(match.player1, match.player2)
                match.winner = winner
                match.loser = loser
                tournament.matches.append(match)
                
                # Update player states
                loser.eliminated = True
                winner.current_round = self._get_next_round(round_name)
                
                winners.append(winner)
            current_players = winners
            if round_name == Round.F:
                break
        
        # Set tournament winner
        if current_players:
            tournament.winner = current_players[0]
            tournament.winner.current_round = Round.W
            tournament.completed = True
        
        return tournament.winner
    
    def _create_matches_for_round(self, players: List[Player], round_name: Round) -> List[Match]:
        """Create matches for the current round."""
        matches = []
        for i in range(0, len(players), 2):
            if i + 1 < len(players):
                match = Match(players[i], players[i + 1], round_name)
                matches.append(match)
        return matches
    
    def _get_next_round(self, current_round: Round) -> Round:
        """Get the next round after current match round."""
        round_progression = {
            Round.R1: Round.R2,
            Round.R2: Round.R3,
            Round.R3: Round.R4,
            Round.R4: Round.QF,
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
        men_winner = self.simulate_tournament(self.men_tournament)
        
        # Simulate women's tournament
        women_winner = self.simulate_tournament(self.women_tournament)
        
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
        print(f"Running {num_simulations} simulations using fixed draw with Elo match simulation...")
        
        all_results = []
        men_winners = Counter()
        women_winners = Counter()
        men_finalists = Counter()
        women_finalists = Counter()
        men_semifinalists = Counter()
        women_semifinalists = Counter()
        
        for _ in tqdm(range(num_simulations), desc="Simulating tournaments"):
            # Reset tournaments for fresh simulation
            self.men_tournament.reset()
            self.women_tournament.reset()
            
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
    
    def set_surface(self, surface: str):
        """Set the surface and update match simulator."""
        self.surface = surface
        self.match_simulator = create_match_simulator(surface=surface)
    
    def set_custom_weights(self, weights: EloWeights):
        """Set custom Elo weights for match simulation."""
        self.match_simulator.set_weights(weights)
    
    def print_simulation_summary(self, stats: Dict) -> None:
        """Print a summary of simulation results."""
        print(f"\n{'='*60}")
        print(f"FIXED DRAW ELO SIMULATION SUMMARY ({stats['total_simulations']} simulations)")
        print(f"Using fixed draw structure from import files with Elo-based match simulation")
        print(f"Surface: {self.surface}")
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
    
    def print_draw_structure(self, gender: Gender = Gender.MEN):
        """Print the draw structure for verification."""
        draw_structure = self.parser.men_draw_structure if gender == Gender.MEN else self.parser.women_draw_structure
        tournament = self.men_tournament if gender == Gender.MEN else self.women_tournament
        
        print(f"\n{gender.value.upper()} DRAW STRUCTURE:")
        print("=" * 50)
        
        for i, section in enumerate(draw_structure, 1):
            print(f"\nSection {i}:")
            print("-" * 20)
            for j, player_name in enumerate(section, 1):
                print(f"  {j}. {player_name}")
        
        if tournament:
            print(f"\nTotal players in tournament: {len(tournament.players)}")

    def print_full_bracket(self, tournament):
        """
        Print the full tournament bracket for a single simulation in a text-based tree format.
        """
        from collections import defaultdict
        
        # Organize matches by round
        rounds = defaultdict(list)
        for match in tournament.matches:
            rounds[match.round].append(match)
        
        # Sort rounds in order
        round_order = [
            Round.R1, Round.R2, Round.R3, Round.R4, Round.QF, Round.SF, Round.F
        ]
        round_names = {
            Round.R1: "Round 1",
            Round.R2: "Round 2",
            Round.R3: "Round 3",
            Round.R4: "Round 4",
            Round.QF: "Quarterfinals",
            Round.SF: "Semifinals",
            Round.F: "Final"
        }
        
        # Prepare bracket lines for each round
        bracket_lines = []
        for rnd in round_order:
            matches = rounds.get(rnd, [])
            if not matches:
                continue
            lines = []
            for match in matches:
                p1 = match.player1.name
                p2 = match.player2.name
                winner = match.winner.name if match.winner else "?"
                lines.append(f"{p1} vs {p2}  ->  {winner}")
            bracket_lines.append((round_names[rnd], lines))
        
        # Print bracket
        print("\n================ TOURNAMENT BRACKET ================")
        for round_name, lines in bracket_lines:
            print(f"\n{round_name}:")
            print("-" * 40)
            for line in lines:
                print(line)
        print("\nWinner:", tournament.winner.name if tournament.winner else "?")
        print("===================================================\n")

    def get_bracket_tree(self, tournament):
        """
        Return the bracket as a nested tree structure for graphical visualization.
        Each node is a dict: { 'name': match_label, 'children': [left, right], 'round': round_name, 'winner': winner_name }
        """
        from collections import defaultdict, OrderedDict
        # Organize matches by round
        rounds = defaultdict(list)
        for match in tournament.matches:
            rounds[match.round].append(match)
        # Sort rounds in order
        round_order = [
            Round.R1, Round.R2, Round.R3, Round.R4, Round.QF, Round.SF, Round.F
        ]
        # Build nodes for each match in each round
        match_nodes = OrderedDict()
        for rnd in round_order:
            for match in rounds.get(rnd, []):
                label = f"{match.player1.name} vs {match.player2.name}"
                winner = match.winner.name if match.winner else "?"
                match_nodes[(rnd, match.player1.name, match.player2.name)] = {
                    'name': label,
                    'children': [],
                    'round': rnd,
                    'winner': winner,
                    'p1': match.player1.name,
                    'p2': match.player2.name
                }
        # Link children: for each match in round N+1, find the two matches in round N whose winner is a player in this match
        for i in range(1, len(round_order)):
            this_round = round_order[i]
            prev_round = round_order[i-1]
            for key, node in match_nodes.items():
                rnd, p1, p2 = key
                if rnd != this_round:
                    continue
                # Find child matches in previous round whose winner is p1 or p2
                children = []
                for prev_key, prev_node in match_nodes.items():
                    prnd, pp1, pp2 = prev_key
                    if prnd != prev_round:
                        continue
                    if prev_node['winner'] == p1 or prev_node['winner'] == p2:
                        children.append(prev_node)
                node['children'] = children
        # The root is the final match
        final_matches = [n for k, n in match_nodes.items() if k[0] == Round.F]
        root = final_matches[0] if final_matches else {'name': 'No final', 'children': [], 'round': Round.F, 'winner': '?'}
        return root


def run_fixed_draw_elo_simulation(
    num_simulations: int = 1000,
    tournament_name: str = "Wimbledon",
    surface: str = "grass"
) -> FixedDrawEloSimulator:
    """Convenience function to run fixed draw Elo simulations."""
    
    # Create simulator
    simulator = FixedDrawEloSimulator(tournament_name, surface)
    simulator.setup_tournaments()
    
    # Run simulations
    stats = simulator.run_multiple_simulations(num_simulations)
    
    # Print summary
    simulator.print_simulation_summary(stats)
    
    return simulator 