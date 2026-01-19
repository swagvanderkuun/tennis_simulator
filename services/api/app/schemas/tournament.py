"""
Tournament and draw schemas
"""
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class Tournament(BaseModel):
    """Tournament schema"""
    id: int
    name: str
    tour: str
    season_year: int
    surface: Optional[str] = None
    source_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class DrawSnapshot(BaseModel):
    """Draw snapshot schema"""
    id: int
    source_id: int
    scraped_at: datetime
    status: str
    
    class Config:
        from_attributes = True


class DrawMatch(BaseModel):
    """Draw match schema"""
    id: int
    round: str
    match_index: int
    player1_name: Optional[str] = None
    player2_name: Optional[str] = None
    player1_bye: bool = False
    player2_bye: bool = False
    child_match1_id: Optional[int] = None
    child_match2_id: Optional[int] = None
    player1_prob: Optional[float] = None
    player2_prob: Optional[float] = None
    winner: Optional[str] = None
    
    class Config:
        from_attributes = True


class DrawEntry(BaseModel):
    """Draw entry (player in draw)"""
    id: int
    part_index: int
    slot_index: int
    seed_text: Optional[str] = None
    player_name: str
    is_bye: bool = False
    
    class Config:
        from_attributes = True


class TournamentProbabilities(BaseModel):
    """Tournament probabilities for a player"""
    player_name: str
    win_prob: float
    final_prob: float
    semi_prob: float
    qf_prob: float


