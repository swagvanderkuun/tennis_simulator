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

from ..core.models import Player, Match


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
    elo_weight: float = 0.1      # Overall Elo weight
    helo_weight: float = 0.1     # Hard court Elo weight
    celo_weight: float = 0.0     # Clay court Elo weight
    gelo_weight: float = 0.4     # Grass court Elo weight
    yelo_weight: float = 0.4     # Year-to-date Elo weight
    form_k: float = 0.03         # Form steepness parameter (k)
    form_alpha: float = 0.95     # Form weight parameter (α) - weight for standard vs form probability
    
    def __post_init__(self):
        """Validate that weights sum to 1.0"""
        total_weight = (self.elo_weight + self.helo_weight + 
                       self.celo_weight + self.gelo_weight + self.yelo_weight)
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(f"Elo weights must sum to 1.0, got {total_weight}")
        
        # Validate form parameters
        if self.form_k <= 0:
            raise ValueError(f"Form steepness (k) must be positive, got {self.form_k}")
        if not 0 <= self.form_alpha <= 1:
            raise ValueError(f"Form weight (α) must be between 0 and 1, got {self.form_alpha}")


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
        weighted_sum = 0.0
        
        # Add weighted contributions from each Elo type
        if player.elo is not None:
            weighted_sum += self.weights.elo_weight * player.elo
        
        if player.helo is not None:
            weighted_sum += self.weights.helo_weight * player.helo
            
        if player.celo is not None:
            weighted_sum += self.weights.celo_weight * player.celo
            
        if player.gelo is not None:
            weighted_sum += self.weights.gelo_weight * player.gelo
            
        if player.yelo is not None:
            weighted_sum += self.weights.yelo_weight * player.yelo
        
        return weighted_sum
    
    def calculate_form_probability(self, player1: Player, player2: Player) -> float:
        """
        Calculate form-based win probability using the formula:
        P_form = 1 / (1 + e^(-k * (form_player1 - form_player2)))
        
        Args:
            player1: First player
            player2: Second player
            
        Returns:
            Form-based probability that player1 wins (0.0 to 1.0)
        """
        # Get form values, default to 0 if not available
        form1 = getattr(player1, 'form', 0.0) or 0.0
        form2 = getattr(player2, 'form', 0.0) or 0.0
        
        # Calculate form difference
        form_diff = form1 - form2
        
        # Apply form formula: P_form = 1 / (1 + e^(-k * form_diff))
        form_probability = 1 / (1 + math.exp(-self.weights.form_k * form_diff))
        
        return form_probability
    
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
        Calculate the probability that player1 beats player2 using blended Elo and form probabilities.
        
        Formula: P_new = α * P_standard + (1-α) * P_form
        For men: Apply five-set probability adjustment after blending
        
        Args:
            player1: First player
            player2: Second player
            gender: 'men' or 'women' to determine if five-set adjustment is applied
            
        Returns:
            Blended probability that player1 wins (0.0 to 1.0)
        """
        # Calculate standard Elo-based probability
        rating1 = self.calculate_weighted_rating(player1)
        rating2 = self.calculate_weighted_rating(player2)
        rating_diff = rating2 - rating1
        p_standard = 1 / (1 + math.pow(10, rating_diff / 400))
        
        # Calculate form-based probability
        p_form = self.calculate_form_probability(player1, player2)
        
        # Blend probabilities: P_new = α * P_standard + (1-α) * P_form
        p_blended = (self.weights.form_alpha * p_standard + 
                    (1 - self.weights.form_alpha) * p_form)
        
        # Apply five-set adjustment for men only
        if gender.lower() == 'men':
            p_blended = five_set_probability(p_blended)
        
        return p_blended
    
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
        
        # Calculate individual components for match details
        p1_standard = self._calculate_standard_probability(player1, player2)
        p1_form = self.calculate_form_probability(player1, player2)
        p2_standard = 1 - p1_standard
        p2_form = 1 - p1_form
        
        # Calculate blended probability before five-set adjustment (for details)
        p1_blended_before = (self.weights.form_alpha * p1_standard + 
                           (1 - self.weights.form_alpha) * p1_form)
        
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
            'rating_difference': self.calculate_weighted_rating(player2) - self.calculate_weighted_rating(player1),
            'weighted_rating_player1': self.calculate_weighted_rating(player1),
            'weighted_rating_player2': self.calculate_weighted_rating(player2),
            # Form-related details
            'player1_standard_probability': p1_standard,
            'player2_standard_probability': p2_standard,
            'player1_form_probability': p1_form,
            'player2_form_probability': p2_form,
            'player1_blended_before_five_set': p1_blended_before,
            'player1_form': getattr(player1, 'form', None),
            'player2_form': getattr(player2, 'form', None),
            'form_difference': (getattr(player1, 'form', 0.0) or 0.0) - (getattr(player2, 'form', 0.0) or 0.0),
            'form_weight_alpha': self.weights.form_alpha,
            'form_steepness_k': self.weights.form_k,
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
                elo_weight=0.3,
                helo_weight=0.4,  # Higher weight for hard court
                celo_weight=0.1,
                gelo_weight=0.1,
                yelo_weight=0.1,
                form_k=0.1,
                form_alpha=0.7
            ),
            'clay': EloWeights(
                elo_weight=0.3,
                helo_weight=0.1,
                celo_weight=0.4,  # Higher weight for clay court
                gelo_weight=0.1,
                yelo_weight=0.1,
                form_k=0.1,
                form_alpha=0.7
            ),
            'grass': EloWeights(
                elo_weight=0.3,
                helo_weight=0.1,
                celo_weight=0.1,
                gelo_weight=0.4,  # Higher weight for grass court
                yelo_weight=0.1,
                form_k=0.1,
                form_alpha=0.7
            ),
            'overall': EloWeights(
                elo_weight=0.4,
                helo_weight=0.2,
                celo_weight=0.2,
                gelo_weight=0.1,
                yelo_weight=0.1,
                form_k=0.1,
                form_alpha=0.7
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