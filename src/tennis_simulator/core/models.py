"""
Core data models for the tennis simulator.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List
from enum import Enum
import random


class Tier(Enum):
    """Player tier enumeration."""
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class Gender(Enum):
    """Gender enumeration for tournaments."""
    MEN = "men"
    WOMEN = "women"


class Round(Enum):
    """Tournament round enumeration."""
    R1 = "R1"    # Round 1 (previously R64)
    R2 = "R2"    # Round 2 (previously R32)
    R3 = "R3"    # Round 3 (previously R16)
    R4 = "R4"    # Round 4 (previously QF)
    QF = "QF"    # Quarter Finals (previously SF)
    SF = "SF"    # Semi Finals (previously F)
    F = "F"      # Final (previously F)
    W = "W"      # Winner (previously F)


@dataclass
class Player:
    """Represents a tennis player with all their attributes."""
    
    name: str
    country: str
    seeding: Optional[int]
    tier: Tier
    elo: Optional[float] = None
    helo: Optional[float] = None
    celo: Optional[float] = None
    gelo: Optional[float] = None
    yelo: Optional[float] = None
    atp_rank: Optional[int] = None
    wta_rank: Optional[int] = None
    current_round: Round = Round.R1
    eliminated: bool = False
    points_earned: int = 0
    
    def get_clean_name(self) -> str:
        """Get player name without seeding information."""
        return self.name
    
    def get_primary_rank(self) -> Optional[int]:
        """Get the primary ranking (ATP for men, WTA for women)."""
        return self.atp_rank if self.atp_rank is not None else self.wta_rank
    
    def get_best_elo(self) -> Optional[float]:
        """Get the best available Elo rating."""
        # yElo is intentionally ignored in simulations (sparse early season and
        # conceptually different from 52-week Elo).
        return self.elo or self.helo or self.celo or self.gelo
    
    def get_grass_elo(self) -> Optional[float]:
        """Get grass court Elo rating, fallback to general Elo."""
        return self.gelo or self.elo
    
    def is_seeded(self) -> bool:
        """Check if player is seeded."""
        return self.seeding is not None
    
    def __str__(self) -> str:
        seeding_info = f"(#{self.seeding})" if self.seeding else "(unseeded)"
        elo_info = f" [Elo: {self.get_best_elo():.0f}]" if self.get_best_elo() else ""
        return f"{self.name} {seeding_info} ({self.country}){elo_info}"


@dataclass
class Match:
    """Represents a tennis match between two players."""
    
    player1: Player
    player2: Player
    round: Round
    winner: Optional[Player] = None
    loser: Optional[Player] = None
    score: Optional[str] = None
    duration_minutes: Optional[int] = None
    
    def simulate(self, use_elo: bool = True) -> Player:
        """Simulate the match and return the winner."""
        if self.player1.eliminated:
            self.winner = self.player2
            self.loser = self.player1
            return self.player2
        
        if self.player2.eliminated:
            self.winner = self.player1
            self.loser = self.player2
            return self.player1
        
        if use_elo and self.player1.get_best_elo() and self.player2.get_best_elo():
            winner = self._simulate_with_elo()
        else:
            winner = self._simulate_random()
        
        # Update match results
        self.winner = winner
        self.loser = self.player2 if winner == self.player1 else self.player1
        
        # Update player states
        self.loser.eliminated = True
        winner.current_round = self._get_next_round()
        
        return winner
    
    def _simulate_with_elo(self) -> Player:
        """Simulate match using Elo ratings."""
        elo1 = self.player1.get_best_elo()
        elo2 = self.player2.get_best_elo()
        
        if not elo1 or not elo2:
            return self._simulate_random()
        
        # Calculate win probability using Elo difference
        elo_diff = elo1 - elo2
        win_prob1 = 1 / (1 + 10 ** (-elo_diff / 400))
        
        if random.random() < win_prob1:
            return self.player1
        else:
            return self.player2
    
    def _simulate_random(self) -> Player:
        """Simulate match randomly (50/50)."""
        return self.player1 if random.random() < 0.5 else self.player2
    
    def _get_next_round(self) -> Round:
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
        return round_progression.get(self.round, Round.W)
    
    def __str__(self) -> str:
        if self.winner:
            return f"{self.player1.name} vs {self.player2.name} - Winner: {self.winner.name}"
        else:
            return f"{self.player1.name} vs {self.player2.name}"


@dataclass
class Tournament:
    """Represents a tennis tournament."""
    
    name: str
    gender: Gender
    players: List[Player] = field(default_factory=list)
    matches: List[Match] = field(default_factory=list)
    current_round: Round = Round.R1
    completed: bool = False
    winner: Optional[Player] = None
    
    def add_player(self, player: Player) -> None:
        """Add a player to the tournament."""
        self.players.append(player)
    
    def get_players_by_tier(self) -> Dict[Tier, List[Player]]:
        """Get players organized by tier."""
        tiers = {tier: [] for tier in Tier}
        for player in self.players:
            tiers[player.tier].append(player)
        return tiers
    
    def get_active_players(self) -> List[Player]:
        """Get all players who haven't been eliminated."""
        return [p for p in self.players if not p.eliminated]
    
    def get_players_in_round(self, round: Round) -> List[Player]:
        """Get all players who reached at least the specified round."""
        # Define round hierarchy (higher index = later round)
        round_hierarchy = {
            Round.R1: 0,
            Round.R2: 1,
            Round.R3: 2,
            Round.R4: 3,
            Round.QF: 4,
            Round.SF: 5,
            Round.F: 6,
            Round.W: 7
        }
        
        target_level = round_hierarchy.get(round, 0)
        return [p for p in self.players if round_hierarchy.get(p.current_round, 0) >= target_level]
    
    def reset(self) -> None:
        """Reset tournament state."""
        for player in self.players:
            player.current_round = Round.R1
            player.eliminated = False
            player.points_earned = 0
        self.matches.clear()
        self.current_round = Round.R1
        self.completed = False
        self.winner = None
    
    def __str__(self) -> str:
        active_count = len(self.get_active_players())
        total_count = len(self.players)
        return f"{self.name} ({self.gender.value}) - {active_count}/{total_count} players active"


@dataclass
class ScoritoGame:
    """Represents a Scorito game with selected players."""
    
    name: str
    men_selection: Dict[Tier, List[str]] = field(default_factory=dict)
    women_selection: Dict[Tier, List[str]] = field(default_factory=dict)
    men_tournament: Optional[Tournament] = None
    women_tournament: Optional[Tournament] = None
    total_points: int = 0
    
    # New tier-based scoring system
    TIER_SCORING = {
        Tier.A: [10, 20, 30, 40, 60, 80, 100],  # R1, R2, R3, R4, QF, SF, F
        Tier.B: [20, 40, 60, 80, 100, 120, 140],
        Tier.C: [30, 60, 90, 120, 140, 160, 180],
        Tier.D: [60, 90, 120, 160, 180, 200, 200]
    }
    
    def add_player_selection(self, gender: Gender, tier: Tier, player_names: List[str]) -> None:
        """Add player selections for a specific gender and tier."""
        if gender == Gender.MEN:
            self.men_selection[tier] = player_names
        else:
            self.women_selection[gender] = player_names
    
    def calculate_points(self) -> Dict[str, int]:
        """Calculate Scorito points for all selected players using tier-based scoring."""
        points = {
            "men": {"A": 0, "B": 0, "C": 0, "D": 0},
            "women": {"A": 0, "B": 0, "C": 0, "D": 0}
        }
        
        # Calculate men's points
        if self.men_tournament:
            for tier, player_names in self.men_selection.items():
                tier_points = 0
                for name in player_names:
                    player = self._find_player_by_name(self.men_tournament.players, name)
                    if player:
                        tier_points += self._calculate_player_points(player, tier)
                points["men"][tier.value] = tier_points
        
        # Calculate women's points
        if self.women_tournament:
            for tier, player_names in self.women_selection.items():
                tier_points = 0
                for name in player_names:
                    player = self._find_player_by_name(self.women_tournament.players, name)
                    if player:
                        tier_points += self._calculate_player_points(player, tier)
                points["women"][tier.value] = tier_points
        
        # Calculate total
        self.total_points = sum(sum(tier_points.values()) for tier_points in points.values())
        
        return points
    
    def _find_player_by_name(self, players: List[Player], name: str) -> Optional[Player]:
        """Find a player by name."""
        for player in players:
            if player.get_clean_name() == name:
                return player
        return None
    
    def _calculate_player_points(self, player: Player, tier: Tier) -> int:
        """Calculate Scorito points for a single player using tier-based scoring."""
        if player.eliminated:
            return 0
        
        # Map rounds to scoring array indices
        round_to_index = {
            Round.R1: 0,  # Round 1
            Round.R2: 1,  # Round 2
            Round.R3: 2,  # Round 3
            Round.R4: 3,   # Round 4
            Round.QF: 4,   # Round 5
            Round.SF: 5,   # Round 6
            Round.F: 6     # Round 7
        }
        
        round_index = round_to_index.get(player.current_round, 0)
        tier_scoring = self.TIER_SCORING.get(tier, self.TIER_SCORING[Tier.D])
        
        if round_index < len(tier_scoring):
            return tier_scoring[round_index]
        else:
            return 0
    
    def __str__(self) -> str:
        return f"{self.name} - Total Points: {self.total_points}" 