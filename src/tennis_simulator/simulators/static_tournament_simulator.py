"""
Static Tournament Simulator using static database and Elo-based match simulation.
"""

import random
from typing import List, Dict, Optional, Tuple
from collections import defaultdict, Counter
import statistics
from tqdm import tqdm

from ..core.models import (
    Player, Match, Tournament, Round, Gender, Tier, ScoritoGame
)
from ..data.static_database import populate_static_database
from .elo_match_simulator import EloMatchSimulator, EloWeights, create_match_simulator


class StaticTournamentSimulator:
    """
    Tournament simulator that uses static database and Elo-based match simulation.
    Creates realistic tournament draws and simulates matches using configurable Elo weights.
    """
    
    def __init__(self, tournament_name: str = "Wimbledon", surface: str = "grass"):
        self.tournament_name = tournament_name
        self.surface = surface
        self.men_tournament: Optional[Tournament] = None
        self.women_tournament: Optional[Tournament] = None
        self.simulation_results: List[Dict] = []
        self.match_simulator = create_match_simulator(surface=surface)
        
        # Load static databases
        self.men_db = populate_static_database('men')
        self.women_db = populate_static_database('women')
    
    def setup_tournaments(self, num_players: int = 128):
        """Setup tournaments with players from static database."""
        # Get top players by Elo for each gender
        men_players = self._get_top_players('men', num_players)
        women_players = self._get_top_players('women', num_players)
        
        # Create realistic tournament draws
        men_draw = self._create_tournament_draw(men_players)
        women_draw = self._create_tournament_draw(women_players)
        
        # Create tournaments
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
    
    def _get_top_players(self, gender: str, num_players: int) -> List[Player]:
        """Get top players by Elo rating from static database."""
        db = self.men_db if gender == 'men' else self.women_db
        
        # Convert to list of tuples (name, data) and sort by Elo
        players_with_elo = [
            (name, data) for name, data in db.items() 
            if data.elo is not None
        ]
        players_with_elo.sort(key=lambda x: x[1].elo, reverse=True)
        
        # Take top players and convert to Player objects
        top_players = []
        for name, data in players_with_elo[:num_players]:
            player = Player(
                name=name,
                country="N/A",  # Static DB doesn't have country
                seeding=len(top_players) + 1 if len(top_players) < 32 else None,  # Top 32 seeded
                tier=Tier(data.tier),
                elo=data.elo,
                helo=data.helo,
                celo=data.celo,
                gelo=data.gelo,
                yelo=data.yelo,
                atp_rank=data.ranking if hasattr(data, 'ranking') else None,
                wta_rank=data.ranking if hasattr(data, 'ranking') else None
            )
            top_players.append(player)
        
        return top_players
    
    def _create_tournament_draw(self, players: List[Player]) -> List[Player]:
        """Create a realistic tournament draw with seeding."""
        if len(players) == 0:
            return []
        
        # Separate seeded and unseeded players
        seeded_players = [p for p in players if p.seeding is not None]
        unseeded_players = [p for p in players if p.seeding is None]
        
        # Sort seeded players by seeding
        seeded_players.sort(key=lambda p: p.seeding)
        
        # Create draw positions (128-player tournament)
        draw_size = len(players)
        draw_positions = list(range(draw_size))
        
        # Place seeded players in their traditional positions
        seeded_positions = self._get_seeded_positions(draw_size)
        draw = [None] * draw_size
        
        # Place seeded players
        for i, player in enumerate(seeded_players):
            if i < len(seeded_positions):
                pos = seeded_positions[i]
                draw[pos] = player
        
        # Fill remaining positions with unseeded players
        unseeded_idx = 0
        for i in range(draw_size):
            if draw[i] is None and unseeded_idx < len(unseeded_players):
                draw[i] = unseeded_players[unseeded_idx]
                unseeded_idx += 1
        
        return [p for p in draw if p is not None]
    
    def _get_seeded_positions(self, draw_size: int) -> List[int]:
        """Get traditional seeding positions for a tournament draw."""
        if draw_size == 128:
            # Traditional 128-player draw seeding positions
            return [
                0,    # 1st seed
                127,  # 2nd seed
                64,   # 3rd seed
                63,   # 4th seed
                32,   # 5th seed
                95,   # 6th seed
                96,   # 7th seed
                31,   # 8th seed
                16,   # 9th seed
                111,  # 10th seed
                80,   # 11th seed
                47,   # 12th seed
                48,   # 13th seed
                79,   # 14th seed
                112,  # 15th seed
                15,   # 16th seed
                8,    # 17th seed
                119,  # 18th seed
                72,   # 19th seed
                55,   # 20th seed
                40,   # 21st seed
                87,   # 22nd seed
                88,   # 23rd seed
                39,   # 24th seed
                56,   # 25th seed
                71,   # 26th seed
                120,  # 27th seed
                7,    # 28th seed
                24,   # 29th seed
                103,  # 30th seed
                104,  # 31st seed
                23,   # 32nd seed
            ]
        else:
            # For smaller draws, use simple positioning
            return list(range(min(32, draw_size)))
    
    def simulate_tournament(self, tournament: Tournament) -> Player:
        """Simulate a complete tournament and return the winner."""
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
            
            # Create matches for current round
            matches = self._create_matches_for_round(current_players, round_name)
            
            # Simulate matches
            winners = []
            for match in matches:
                winner, loser, details = self.match_simulator.simulate_match(match.player1, match.player2)
                match.winner = winner
                match.loser = loser
                tournament.matches.append(match)
                winners.append(winner)
            
            # Update current players and round
            current_players = winners
        
        # Set tournament winner
        if current_players:
            tournament.winner = current_players[0]
            tournament.winner.current_round = Round.W
            tournament.completed = True
        
        return tournament.winner
    
    def _create_matches_for_round(self, players: List[Player], round_name: Round) -> List[Match]:
        """Create matches for a specific round."""
        matches = []
        
        # Create matches by pairing consecutive players
        for i in range(0, len(players), 2):
            if i + 1 < len(players):
                match = Match(
                    player1=players[i],
                    player2=players[i + 1],
                    round=round_name
                )
                matches.append(match)
        
        return matches
    
    def run_single_simulation(self) -> Dict:
        """Run a single tournament simulation."""
        if not self.men_tournament or not self.women_tournament:
            self.setup_tournaments()
        
        # Simulate both tournaments
        men_winner = self.simulate_tournament(self.men_tournament)
        women_winner = self.simulate_tournament(self.women_tournament)
        
        # Collect results
        result = {
            'men_winner': men_winner.name,
            'women_winner': women_winner.name,
            'men_tournament': self.men_tournament,
            'women_tournament': self.women_tournament,
            'surface': self.surface
        }
        
        self.simulation_results.append(result)
        return result
    
    def run_multiple_simulations(self, num_simulations: int = 1000) -> Dict:
        """Run multiple tournament simulations and collect statistics."""
        print(f"Running {num_simulations} simulations on {self.surface} surface...")
        
        # Setup tournaments once
        if not self.men_tournament or not self.women_tournament:
            self.setup_tournaments()
        
        men_winners = []
        women_winners = []
        
        # Run simulations
        for i in tqdm(range(num_simulations), desc="Simulating tournaments"):
            # Reset tournaments
            self.men_tournament.reset()
            self.women_tournament.reset()
            
            # Simulate
            men_winner = self.simulate_tournament(self.men_tournament)
            women_winner = self.simulate_tournament(self.women_tournament)
            
            men_winners.append(men_winner.name)
            women_winners.append(women_winner.name)
        
        # Calculate statistics
        men_winner_counts = Counter(men_winners)
        women_winner_counts = Counter(women_winners)
        
        stats = {
            'num_simulations': num_simulations,
            'surface': self.surface,
            'men_winners': dict(men_winner_counts),
            'women_winners': dict(women_winner_counts),
            'men_most_likely_winner': men_winner_counts.most_common(1)[0] if men_winner_counts else None,
            'women_most_likely_winner': women_winner_counts.most_common(1)[0] if women_winner_counts else None,
            'men_winner_probabilities': {name: count/num_simulations for name, count in men_winner_counts.items()},
            'women_winner_probabilities': {name: count/num_simulations for name, count in women_winner_counts.items()}
        }
        
        return stats
    
    def get_player_recommendations(self, gender: Gender, tier: Tier, num_recommendations: int = 5) -> List[Tuple[Player, Dict]]:
        """Get player recommendations based on Elo ratings and tier."""
        db = self.men_db if gender == Gender.MEN else self.women_db
        
        # Filter players by tier and sort by Elo
        tier_players = [
            (name, data) for name, data in db.items()
            if data.tier == tier.value and data.elo is not None
        ]
        tier_players.sort(key=lambda x: x[1].elo, reverse=True)
        
        recommendations = []
        for name, data in tier_players[:num_recommendations]:
            player = Player(
                name=name,
                country="N/A",
                seeding=None,
                tier=Tier(data.tier),
                elo=data.elo,
                helo=data.helo,
                celo=data.celo,
                gelo=data.gelo,
                yelo=data.yelo,
                atp_rank=data.ranking if hasattr(data, 'ranking') else None,
                wta_rank=data.ranking if hasattr(data, 'ranking') else None
            )
            
            # Calculate surface-specific rating
            surface_rating = self.match_simulator.calculate_weighted_rating(player)
            
            recommendations.append((player, {
                'surface_rating': surface_rating,
                'elo': data.elo,
                'tier': data.tier
            }))
        
        return recommendations
    
    def set_surface(self, surface: str):
        """Change the surface and update the match simulator."""
        self.surface = surface
        self.match_simulator = create_match_simulator(surface=surface)
    
    def set_custom_weights(self, weights: EloWeights):
        """Set custom Elo weights for match simulation."""
        self.match_simulator = EloMatchSimulator(weights=weights)
    
    def print_simulation_summary(self, stats: Dict) -> None:
        """Print a summary of simulation results."""
        print(f"\n=== {self.tournament_name} Simulation Results ===")
        print(f"Surface: {stats['surface']}")
        print(f"Number of simulations: {stats['num_simulations']}")
        
        print(f"\nMen's Tournament:")
        if stats['men_most_likely_winner']:
            winner, count = stats['men_most_likely_winner']
            prob = count / stats['num_simulations']
            print(f"  Most likely winner: {winner} ({prob:.1%})")
        
        print(f"\nWomen's Tournament:")
        if stats['women_most_likely_winner']:
            winner, count = stats['women_most_likely_winner']
            prob = count / stats['num_simulations']
            print(f"  Most likely winner: {winner} ({prob:.1%})")
        
        print(f"\nTop 5 Men's Winners:")
        men_sorted = sorted(stats['men_winners'].items(), key=lambda x: x[1], reverse=True)
        for i, (player, count) in enumerate(men_sorted[:5]):
            prob = count / stats['num_simulations']
            print(f"  {i+1}. {player}: {prob:.1%}")
        
        print(f"\nTop 5 Women's Winners:")
        women_sorted = sorted(stats['women_winners'].items(), key=lambda x: x[1], reverse=True)
        for i, (player, count) in enumerate(women_sorted[:5]):
            prob = count / stats['num_simulations']
            print(f"  {i+1}. {player}: {prob:.1%}")


def run_static_tournament_simulation(
    num_simulations: int = 1000,
    tournament_name: str = "Wimbledon",
    surface: str = "grass"
) -> StaticTournamentSimulator:
    """
    Convenience function to run a complete tournament simulation.
    
    Args:
        num_simulations: Number of simulations to run
        tournament_name: Name of the tournament
        surface: Surface type ('grass', 'clay', 'hard', 'overall')
        
    Returns:
        StaticTournamentSimulator with results
    """
    simulator = StaticTournamentSimulator(tournament_name, surface)
    stats = simulator.run_multiple_simulations(num_simulations)
    simulator.print_simulation_summary(stats)
    return simulator 