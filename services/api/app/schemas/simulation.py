"""
Simulation schemas
"""
from typing import Optional, Dict, List
from pydantic import BaseModel


class EloWeights(BaseModel):
    """Elo weights configuration"""
    elo_weight: float = 0.45
    helo_weight: float = 0.25
    celo_weight: float = 0.20
    gelo_weight: float = 0.10
    form_elo_scale: float = 1.0
    form_elo_cap: float = 80.0


class MatchSimRequest(BaseModel):
    """Match simulation request"""
    player1_name: str
    player2_name: str
    tour: str = "atp"
    surface: Optional[str] = None
    weights: Optional[EloWeights] = None


class SimulationFactor(BaseModel):
    """Factor contributing to match prediction"""
    name: str
    player1_value: float
    player2_value: float
    weight: float
    contribution: float


class MatchSimResult(BaseModel):
    """Match simulation result"""
    player1_name: str
    player2_name: str
    player1_win_prob: float
    player2_win_prob: float
    winner_name: str
    loser_name: str
    rating_diff: float
    factors: List[SimulationFactor]


class WeightPreset(BaseModel):
    """Weight preset configuration"""
    name: str
    description: Optional[str] = None
    weights: EloWeights


class ScenarioRequest(BaseModel):
    """Scenario simulation request"""
    tournament_id: int
    weights: EloWeights
    num_simulations: int = 1000


class ScenarioResult(BaseModel):
    """Scenario simulation result"""
    player_name: str
    win_prob: float
    final_prob: float
    semi_prob: float
    qf_prob: float

