"""
Matchups router
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
import math

from app.db.session import get_db
from app.schemas.simulation import MatchSimRequest, MatchSimResult, SimulationFactor
from app.services.match_simulator import EloMatchSimulator, EloWeights, PlayerLite

router = APIRouter()


def build_factors(p1: PlayerLite, p2: PlayerLite, weights: EloWeights) -> List[SimulationFactor]:
    factors = []
    factors.append(SimulationFactor(
        name="Overall Elo",
        player1_value=float(p1.elo or 1500),
        player2_value=float(p2.elo or 1500),
        weight=weights.elo_weight,
        contribution=(float(p1.elo or 1500) - float(p2.elo or 1500)) * weights.elo_weight / 400,
    ))
    factors.append(SimulationFactor(
        name="Hard Court Elo",
        player1_value=float(p1.helo or p1.elo or 1500),
        player2_value=float(p2.helo or p2.elo or 1500),
        weight=weights.helo_weight,
        contribution=(float(p1.helo or p1.elo or 1500) - float(p2.helo or p2.elo or 1500)) * weights.helo_weight / 400,
    ))
    factors.append(SimulationFactor(
        name="Clay Court Elo",
        player1_value=float(p1.celo or p1.elo or 1500),
        player2_value=float(p2.celo or p2.elo or 1500),
        weight=weights.celo_weight,
        contribution=(float(p1.celo or p1.elo or 1500) - float(p2.celo or p2.elo or 1500)) * weights.celo_weight / 400,
    ))
    factors.append(SimulationFactor(
        name="Grass Court Elo",
        player1_value=float(p1.gelo or p1.elo or 1500),
        player2_value=float(p2.gelo or p2.elo or 1500),
        weight=weights.gelo_weight,
        contribution=(float(p1.gelo or p1.elo or 1500) - float(p2.gelo or p2.elo or 1500)) * weights.gelo_weight / 400,
    ))
    # Form adjustment (scale + cap)
    form_diff = float(p1.form or 0.0) - float(p2.form or 0.0)
    form_adj = min(weights.form_elo_cap, abs(form_diff) * weights.form_elo_scale)
    form_adj = form_adj if form_diff > 0 else -form_adj
    factors.append(SimulationFactor(
        name="Form Adjustment",
        player1_value=float(p1.form or 0.0),
        player2_value=float(p2.form or 0.0),
        weight=1.0,
        contribution=form_adj / 400,
    ))
    return factors


@router.post("/simulate", response_model=MatchSimResult)
async def simulate_match(
    request: MatchSimRequest,
    db: Session = Depends(get_db),
):
    """Simulate a match between two players"""
    gender = "men" if request.tour == "atp" else "women"
    if request.weights:
        weights = EloWeights(
            elo_weight=request.weights.elo_weight,
            helo_weight=request.weights.helo_weight,
            celo_weight=request.weights.celo_weight,
            gelo_weight=request.weights.gelo_weight,
            form_elo_scale=request.weights.form_elo_scale,
            form_elo_cap=request.weights.form_elo_cap,
        )
    else:
        weights = EloWeights()
    
    # Get player data with precomputed form (fast path)
    sql = """
        SELECT
          c.player_name as name,
          c.elo, c.helo, c.celo, c.gelo,
          COALESCE(
            c.form,
            0.75 * COALESCE(c.form_4w, 0) + 0.25 * COALESCE(c.form_12w, 0),
            0
          ) AS form
        FROM tennis.elo_current c
        WHERE c.gender = :gender AND c.player_name = ANY(:names)
    """
    
    try:
        result = db.execute(
            text(sql),
            {"gender": gender, "names": [request.player1_name, request.player2_name]},
        )
        rows = {row["name"]: row for row in result.mappings().all()}
        
        if request.player1_name not in rows or request.player2_name not in rows:
            raise HTTPException(status_code=404, detail="Player(s) not found")
        
        p1 = rows[request.player1_name]
        p2 = rows[request.player2_name]
        
        p1_obj = PlayerLite(
            name=request.player1_name,
            tier="D",
            elo=p1["elo"],
            helo=p1.get("helo"),
            celo=p1.get("celo"),
            gelo=p1.get("gelo"),
            form=p1.get("form") or 0.0,
        )
        p2_obj = PlayerLite(
            name=request.player2_name,
            tier="D",
            elo=p2["elo"],
            helo=p2.get("helo"),
            celo=p2.get("celo"),
            gelo=p2.get("gelo"),
            form=p2.get("form") or 0.0,
        )

        simulator = EloMatchSimulator(weights=weights)
        win_prob = simulator.calculate_win_probability(p1_obj, p2_obj, gender)
        factors = build_factors(p1_obj, p2_obj, weights)

        # Simulate match
        import random
        winner = request.player1_name if random.random() < win_prob else request.player2_name
        loser = request.player2_name if winner == request.player1_name else request.player1_name
        
        return MatchSimResult(
            player1_name=request.player1_name,
            player2_name=request.player2_name,
            player1_win_prob=win_prob,
            player2_win_prob=1 - win_prob,
            winner_name=winner,
            loser_name=loser,
            rating_diff=(p1["elo"] or 1500) - (p2["elo"] or 1500),
            factors=factors,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/explain", response_model=List[SimulationFactor])
async def get_match_explanation(
    player1: str = Query(...),
    player2: str = Query(...),
    tour: str = Query("atp"),
    db: Session = Depends(get_db),
):
    """Get explanation factors for a matchup"""
    # Use simulate_match and return just the factors
    request = MatchSimRequest(
        player1_name=player1,
        player2_name=player2,
        tour=tour,
    )
    result = await simulate_match(request, db)
    return result.factors

