"""
Tennis Simulator Package

A comprehensive tennis tournament simulation system for ATP and WTA Grand Slam tournaments.
"""

__version__ = "1.0.0"
__author__ = "Tennis Simulator Team"

from .core.models import Player, Match, Tournament, Round, Gender, Tier, ScoritoGame
from .data.player_database import player_db, PlayerDatabase
from .simulators.tournament_simulator import FixedDrawSimulator, run_tournament_simulation
from .utils.player_selector import PlayerSelector, run_interactive_selector

__all__ = [
    # Core models
    "Player",
    "Match", 
    "Tournament",
    "Round",
    "Gender",
    "Tier",
    "ScoritoGame",
    
    # Database
    "player_db",
    "PlayerDatabase",
    
    # Simulators
    "FixedDrawSimulator",
    "run_tournament_simulation",
    
    # Utilities
    "PlayerSelector",
    "run_interactive_selector",
] 