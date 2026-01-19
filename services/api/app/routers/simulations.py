"""
Simulations router
"""
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.simulation import ScenarioRequest, ScenarioResult, EloWeights, WeightPreset

router = APIRouter()


# Preset configurations
WEIGHT_PRESETS = {
    "Overall (default)": EloWeights(
        elo_weight=0.45, helo_weight=0.25, celo_weight=0.20, gelo_weight=0.10
    ),
    "Hard Court Focus": EloWeights(
        elo_weight=0.25, helo_weight=0.50, celo_weight=0.15, gelo_weight=0.10
    ),
    "Clay Court Focus": EloWeights(
        elo_weight=0.25, helo_weight=0.15, celo_weight=0.50, gelo_weight=0.10
    ),
    "Grass Court Focus": EloWeights(
        elo_weight=0.25, helo_weight=0.15, celo_weight=0.10, gelo_weight=0.50
    ),
    "Elo Only": EloWeights(
        elo_weight=1.0, helo_weight=0.0, celo_weight=0.0, gelo_weight=0.0,
        form_elo_scale=0, form_elo_cap=0
    ),
}


@router.get("/presets", response_model=Dict[str, EloWeights])
async def get_weight_presets():
    """Get all weight presets"""
    return WEIGHT_PRESETS


@router.post("/scenario", response_model=List[ScenarioResult])
async def run_scenario_simulation(
    request: ScenarioRequest,
    db: Session = Depends(get_db),
):
    """Run scenario simulation with custom weights"""
    # Placeholder implementation
    # In production, this would run actual tournament simulations
    return []

