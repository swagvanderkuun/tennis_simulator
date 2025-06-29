"""
Tennis Simulator Package

A comprehensive tennis tournament simulation system with Elo-based match prediction.
"""

__version__ = "1.0.0"
__author__ = "Tennis Simulator Team"

from .core.models import Player, Match, Tournament, Tier, Gender, Round, ScoritoGame
from .data.player_database import PlayerDatabase
from .simulators.tournament_simulator import FixedDrawSimulator
from .simulators.elo_match_simulator import EloMatchSimulator, EloWeights, create_match_simulator
from .utils.player_selector import PlayerSelector

__all__ = [
    # Core models
    "Player", "Match", "Tournament", "Tier", "Gender", "Round", "ScoritoGame",
    
    # Data management
    "PlayerDatabase",
    
    # Simulators
    "FixedDrawSimulator", "EloMatchSimulator", "EloWeights", "create_match_simulator",
    
    # Utilities
    "PlayerSelector",
] 