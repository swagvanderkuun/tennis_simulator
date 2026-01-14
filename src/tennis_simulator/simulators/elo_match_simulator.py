"""
Elo-based Tennis Match Simulator

This module provides a sophisticated tennis match simulation system based on Elo ratings
with configurable weights for different surface types (hard court, clay, grass) and
year-to-date performance.
"""

import random
import math
import numpy
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

from ..core.models import Player


def five_set_probability(p3: float) -> float:
    """
    Convert best-of-3 probability to best-of-5 probability for men's matches.
    
    Formula:
    - p1 = numpy.roots([-2, 3, 0, -1*p3])[1]  # Single set probability
    - p5 = (p1**3)*(4 - 3*p1 + (6*(1-p1)*(1-p1)))  # Best-of-5 probability
    
    Args:
        p3: Best-of-3 probability (0.0 to 1.0)
        
    Returns:
        Best-of-5 probability (0.0 to 1.0)
    """
    # Find single set probability by solving cubic equation
    # -2*p1^3 + 3*p1^2 - p3 = 0
    roots = numpy.roots([-2, 3, 0, -1*p3])
    
    # Take the real root between 0 and 1
    p1 = None
    for root in roots:
        if abs(root.imag) < 1e-10 and 0 <= root.real <= 1:
            p1 = root.real
            break
    
    if p1 is None:
        # Fallback: use p3 directly if no valid root found
        return p3
    
    # Calculate best-of-5 probability
    p5 = (p1**3) * (4 - 3*p1 + (6*(1-p1)*(1-p1)))
    
    # Ensure result is between 0 and 1
    return max(0.0, min(1.0, p5))


@dataclass
class EloWeights:
    """Configuration for Elo rating weights in match simulation"""
    # Rating blend (must sum to 1.0)
    elo_weight: float = 0.45      # Overall Elo weight
    helo_weight: float = 0.25     # Hard court Elo weight
    celo_weight: float = 0.20     # Clay court Elo weight
    gelo_weight: float = 0.10     # Grass court Elo weight

    # Form -> Elo adjustment
    # `player.form` is expected to be an Elo-point adjustment derived from Elo movement
    # over time (e.g. 4w/12w delta blend). We optionally scale and clamp it here.
    form_elo_scale: float = 1.0
    form_elo_cap: float = 80.0
    
    def __post_init__(self):
        """Validate that weights sum to 1.0"""
        total_weight = (self.elo_weight + self.helo_weight +
                        self.celo_weight + self.gelo_weight)
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(f"Elo weights must sum to 1.0, got {total_weight}")

        if self.form_elo_scale < 0:
            raise ValueError(f"form_elo_scale must be >= 0, got {self.form_elo_scale}")
        if self.form_elo_cap < 0:
            raise ValueError(f"form_elo_cap must be >= 0, got {self.form_elo_cap}")


class EloMatchSimulator:
    """
    Elo-based tennis match simulator with configurable surface weights.
    
    Uses the standard Elo formula: P(A beats B) = 1 / (1 + 10^((B_rating - A_rating) / 400))
    """
    
    def __init__(self, weights: Optional[EloWeights] = None):
        """
        Initialize the simulator with optional custom weights.
        
        Args:
            weights: EloWeights configuration. If None, uses default weights.
        """
        self.weights = weights or EloWeights()
    
    def calculate_weighted_rating(self, player: Player) -> float:
        """
        Calculate the weighted Elo rating for a player based on configured weights.
        
        Args:
            player: Player object with Elo ratings
            
        Returns:
            Weighted Elo rating
        """
        # IMPORTANT: Do not bias probabilities due to missing surface components.
        # If a component is missing, fall back to a reasonable "base" rating rather than
        # dropping its weight from the sum. This keeps the total weight consistent and
        # avoids systematic under/over-rating players with NULL columns.

        base = (
            player.elo
            if player.elo is not None
            else (player.helo if player.helo is not None else (player.celo if player.celo is not None else player.gelo))
        )
        if base is None:
            # Neutral baseline; absolute value cancels in Elo diffs if both are missing,
            # but provides sane behavior when only one player is missing all ratings.
            base = 1500.0

        elo = player.elo if player.elo is not None else base
        helo = player.helo if player.helo is not None else base
        celo = player.celo if player.celo is not None else base
        gelo = player.gelo if player.gelo is not None else base

        return (
            self.weights.elo_weight * float(elo)
            + self.weights.helo_weight * float(helo)
            + self.weights.celo_weight * float(celo)
            + self.weights.gelo_weight * float(gelo)
        )

    def calculate_form_elo_adjustment(self, player: Player) -> float:
        """
        Convert rank-based `player.form` to an Elo-point adjustment (clamped).

        `player.form` should be derived from weekly Elo movement (Elo points).
        Positive means improving, negative means declining.
        """
        raw = getattr(player, "form", 0.0) or 0.0
        try:
            raw_f = float(raw)
        except Exception:
            raw_f = 0.0

        adj = raw_f * float(self.weights.form_elo_scale)
        cap = float(self.weights.form_elo_cap)
        if cap > 0:
            adj = max(-cap, min(cap, adj))
        return adj
    
    def _calculate_standard_probability(self, player1: Player, player2: Player) -> float:
        """
        Calculate standard Elo-based win probability (without form blending).
        
        Args:
            player1: First player
            player2: Second player
            
        Returns:
            Standard Elo probability that player1 wins (0.0 to 1.0)
        """
        rating1 = self.calculate_weighted_rating(player1)
        rating2 = self.calculate_weighted_rating(player2)
        rating_diff = rating2 - rating1
        return 1 / (1 + math.pow(10, rating_diff / 400))
    
    def calculate_win_probability(self, player1: Player, player2: Player, gender: str = 'women') -> float:
        """
        Calculate win probability using *effective* Elo:
          Elo* = weighted_surface_elo + form_elo_adjustment

        For men: apply five-set probability adjustment to the final probability.
        
        Args:
            player1: First player
            player2: Second player
            gender: 'men' or 'women' to determine if five-set adjustment is applied
            
        Returns:
            Probability that player1 wins (0.0 to 1.0)
        """
        rating1 = self.calculate_weighted_rating(player1) + self.calculate_form_elo_adjustment(player1)
        rating2 = self.calculate_weighted_rating(player2) + self.calculate_form_elo_adjustment(player2)
        rating_diff = rating2 - rating1
        p = 1 / (1 + math.pow(10, rating_diff / 400))

        if gender.lower() == 'men':
            p = five_set_probability(p)

        return p
    
    def simulate_match(self, player1: Player, player2: Player, gender: str = 'women') -> Tuple[Player, Player, Dict]:
        """
        Simulate a tennis match between two players.
        
        Args:
            player1: First player
            player2: Second player
            gender: 'men' or 'women' to determine if five-set adjustment is applied
            
        Returns:
            Tuple of (winner, loser, match_details)
        """
        # Calculate win probabilities
        p1_win_prob = self.calculate_win_probability(player1, player2, gender)
        p2_win_prob = 1 - p1_win_prob
        
        # Components for match details
        p1_standard = self._calculate_standard_probability(player1, player2)
        p2_standard = 1 - p1_standard

        base1 = self.calculate_weighted_rating(player1)
        base2 = self.calculate_weighted_rating(player2)
        form_adj1 = self.calculate_form_elo_adjustment(player1)
        form_adj2 = self.calculate_form_elo_adjustment(player2)
        eff1 = base1 + form_adj1
        eff2 = base2 + form_adj2
        
        # Determine winner based on probabilities
        if random.random() < p1_win_prob:
            winner, loser = player1, player2
            winner_prob = p1_win_prob
        else:
            winner, loser = player2, player1
            winner_prob = p2_win_prob
        
        # Create match details
        match_details = {
            'player1_win_probability': p1_win_prob,
            'player2_win_probability': p2_win_prob,
            'winner_probability': winner_prob,
            'rating_difference': eff2 - eff1,
            'weighted_rating_player1': base1,
            'weighted_rating_player2': base2,
            'effective_rating_player1': eff1,
            'effective_rating_player2': eff2,
            # Form-related details
            'player1_standard_probability': p1_standard,
            'player2_standard_probability': p2_standard,
            'player1_form_raw': getattr(player1, 'form', None),
            'player2_form_raw': getattr(player2, 'form', None),
            'player1_form_elo_adjustment': form_adj1,
            'player2_form_elo_adjustment': form_adj2,
            'form_elo_scale': self.weights.form_elo_scale,
            'form_elo_cap': self.weights.form_elo_cap,
            'gender': gender,
            'five_set_adjusted': gender.lower() == 'men'
        }
        
        return winner, loser, match_details
    
    def get_surface_specific_weights(self, surface: str) -> EloWeights:
        """
        Get pre-configured weights optimized for specific surfaces.
        
        Args:
            surface: Surface type ('hard', 'clay', 'grass', 'overall')
            
        Returns:
            EloWeights configuration for the surface
        """
        surface_weights = {
            'hard': EloWeights(
                elo_weight=0.30,
                helo_weight=0.45,  # Higher weight for hard court
                celo_weight=0.15,
                gelo_weight=0.10,
                form_elo_scale=self.weights.form_elo_scale,
                form_elo_cap=self.weights.form_elo_cap
            ),
            'clay': EloWeights(
                elo_weight=0.30,
                helo_weight=0.15,
                celo_weight=0.45,  # Higher weight for clay court
                gelo_weight=0.10,
                form_elo_scale=self.weights.form_elo_scale,
                form_elo_cap=self.weights.form_elo_cap
            ),
            'grass': EloWeights(
                elo_weight=0.30,
                helo_weight=0.15,
                celo_weight=0.10,
                gelo_weight=0.45,  # Higher weight for grass court
                form_elo_scale=self.weights.form_elo_scale,
                form_elo_cap=self.weights.form_elo_cap
            ),
            'overall': EloWeights(
                elo_weight=0.45,
                helo_weight=0.25,
                celo_weight=0.20,
                gelo_weight=0.10,
                form_elo_scale=self.weights.form_elo_scale,
                form_elo_cap=self.weights.form_elo_cap
            )
        }
        
        return surface_weights.get(surface.lower(), EloWeights())
    
    def set_surface_weights(self, surface: str):
        """
        Update the simulator weights for a specific surface.
        
        Args:
            surface: Surface type ('hard', 'clay', 'grass', 'overall')
        """
        self.weights = self.get_surface_specific_weights(surface)

    def set_weights(self, weights: EloWeights):
        """Set new Elo weights for the match simulator."""
        self.weights = weights


def create_match_simulator(weights: Optional[EloWeights] = None, surface: Optional[str] = None) -> EloMatchSimulator:
    """
    Factory function to create a match simulator with specified configuration.
    
    Args:
        weights: Custom EloWeights configuration
        surface: Surface type for pre-configured weights ('hard', 'clay', 'grass', 'overall')
        
    Returns:
        Configured EloMatchSimulator instance
    """
    if weights and surface:
        raise ValueError("Cannot specify both weights and surface")
    
    if surface:
        # Create a temporary instance to get surface-specific weights
        temp_sim = EloMatchSimulator()
        surface_weights = temp_sim.get_surface_specific_weights(surface)
        return EloMatchSimulator(weights=surface_weights)
    else:
        return EloMatchSimulator(weights=weights) 