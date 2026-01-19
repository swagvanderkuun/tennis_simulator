"""
Player schemas
"""
from typing import Optional, List
from pydantic import BaseModel
from datetime import date


class PlayerBase(BaseModel):
    """Base player schema"""
    name: str
    tier: str = "D"
    country: Optional[str] = None


class PlayerCreate(PlayerBase):
    """Schema for creating a player"""
    elo: Optional[float] = None
    helo: Optional[float] = None
    celo: Optional[float] = None
    gelo: Optional[float] = None


class Player(PlayerBase):
    """Full player schema"""
    id: int
    elo: Optional[float] = None
    helo: Optional[float] = None
    celo: Optional[float] = None
    gelo: Optional[float] = None
    ranking: Optional[int] = None
    elo_rank: Optional[int] = None
    form: Optional[float] = None
    
    class Config:
        from_attributes = True


class PlayerEloHistoryPoint(BaseModel):
    """Single point in Elo history"""
    date: str
    elo: float
    helo: Optional[float] = None
    celo: Optional[float] = None
    gelo: Optional[float] = None


class PlayerEloHistory(BaseModel):
    """Elo history for a player"""
    player_id: int
    player_name: str
    history: List[PlayerEloHistoryPoint]


class PlayerFilter(BaseModel):
    """Filter parameters for player queries"""
    tour: Optional[str] = None
    tier: Optional[str] = None
    search: Optional[str] = None
    min_elo: Optional[float] = None
    max_elo: Optional[float] = None
    limit: int = 100
    offset: int = 0


