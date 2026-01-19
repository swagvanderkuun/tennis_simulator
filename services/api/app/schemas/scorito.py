"""
Scorito schemas
"""
from typing import Dict, List, Optional
from pydantic import BaseModel
from app.schemas.simulation import EloWeights


class ScoringRules(BaseModel):
    """Scoring rules by tier"""
    A: List[int] = [10, 20, 30, 40, 60, 80, 100]
    B: List[int] = [20, 40, 60, 80, 100, 120, 140]
    C: List[int] = [30, 60, 90, 120, 140, 160, 180]
    D: List[int] = [60, 90, 120, 160, 180, 200, 200]


class ScoritoRequest(BaseModel):
    """Scorito optimization request"""
    tournament_id: int
    scoring: ScoringRules
    num_simulations: int = 1000
    budget: Optional[float] = None
    weights: Optional[EloWeights] = None


class PathOpponent(BaseModel):
    opponent: str
    meet_prob: float
    win_prob: float


class ScoritoResult(BaseModel):
    """Scorito optimization result for a player"""
    player_name: str
    tier: str
    expected_points: float
    avg_round: float
    win_probability: float
    value_score: float
    
    # Additional stats
    median_round: Optional[float] = None
    mode_round: Optional[str] = None
    eliminator: Optional[str] = None
    elim_rate: Optional[float] = None
    points_std: Optional[float] = None
    points_p10: Optional[float] = None
    points_p50: Optional[float] = None
    points_p90: Optional[float] = None
    risk_adj_value: Optional[float] = None
    form_trend: Optional[float] = None
    path_difficulty_avg: Optional[float] = None
    path_difficulty_peak: Optional[float] = None
    path_rounds: Optional[Dict[str, float]] = None
    path_round_opponents: Optional[Dict[str, List[PathOpponent]]] = None
    elo_sparkline: Optional[List[float]] = None
    elim_round_probs: Optional[Dict[str, float]] = None
    simulation_strength: Optional[float] = None
    path_strength: Optional[float] = None


class ScoritoValuePick(BaseModel):
    """Value pick recommendation"""
    player_name: str
    tier: str
    expected_points: float
    value_score: float
    insight: str

