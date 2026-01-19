"""
Players router
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.db.cache import cache_get, cache_set
from app.schemas.player import Player, PlayerEloHistory, PlayerEloHistoryPoint

router = APIRouter()


@router.get("", response_model=List[Player])
async def get_players(
    tour: Optional[str] = Query(None, description="Tour: atp or wta"),
    tier: Optional[str] = Query(None, description="Tier: A, B, C, or D"),
    search: Optional[str] = Query(None, description="Search by name"),
    limit: int = Query(500, ge=1, le=2000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get list of players with optional filters"""
    gender = "men" if tour == "atp" else "women" if tour == "wta" else None

    cache_key = f"players:{gender}:{tier}:{search}:{limit}:{offset}"
    cached = cache_get(cache_key)
    if cached is not None:
        return [Player(**row) for row in cached]
    
    sql = """
        WITH active_set AS (
            SELECT id FROM tennis.tier_sets
            WHERE gender = :gender AND active = 1
            ORDER BY created_at DESC, id DESC
            LIMIT 1
        )
        SELECT
            c.player_id as id,
            c.player_name as name,
            COALESCE(ta.tier, 'D') as tier,
            c.elo, c.helo, c.celo, c.gelo,
            c.rank as ranking,
            c.elo_rank,
            COALESCE(
                c.form,
                0.75 * COALESCE(c.form_4w, 0) + 0.25 * COALESCE(c.form_12w, 0),
                0
            ) as form
        FROM tennis.elo_current c
        LEFT JOIN active_set s ON true
        LEFT JOIN tennis.tier_assignments ta ON ta.tier_set_id = s.id AND ta.player_id = c.player_id
        WHERE (:gender IS NULL OR c.gender = :gender)
          AND (:tier IS NULL OR COALESCE(ta.tier, 'D') = :tier)
          AND (:search IS NULL OR c.player_name ILIKE :search_pattern)
        ORDER BY c.elo_rank NULLS LAST, c.player_name
        LIMIT :limit OFFSET :offset
    """
    
    try:
        result = db.execute(
            text(sql),
            {
                "gender": gender,
                "tier": tier,
                "search": search,
                "search_pattern": f"%{search}%" if search else None,
                "limit": limit,
                "offset": offset,
            },
        )
        rows = result.mappings().all()
        data = [dict(row) for row in rows]
        cache_set(cache_key, data, ttl=180)
        return [Player(**row) for row in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/form_movers", response_model=List[Player])
async def get_form_movers(
    tour: str = Query(..., description="Tour: atp or wta"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Get players with biggest form changes"""
    gender = "men" if tour == "atp" else "women"

    cache_key = f"players:form_movers:{gender}:{limit}"
    cached = cache_get(cache_key)
    if cached is not None:
        return [Player(**row) for row in cached]
    
    sql = """
        SELECT
            c.player_id as id,
            c.player_name as name,
            'D' as tier,
            c.elo, c.helo, c.celo, c.gelo,
            c.rank as ranking,
            c.elo_rank,
            COALESCE(c.form_4w, 0) as form
        FROM tennis.elo_current c
        WHERE c.gender = :gender
        ORDER BY ABS(COALESCE(c.form_4w, 0)) DESC
        LIMIT :limit
    """
    
    try:
        result = db.execute(text(sql), {"gender": gender, "limit": limit})
        rows = result.mappings().all()
        data = [dict(row) for row in rows]
        cache_set(cache_key, data, ttl=300)
        return [Player(**row) for row in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{player_id}", response_model=Player)
async def get_player(
    player_id: int,
    db: Session = Depends(get_db),
):
    """Get single player by ID"""
    sql = """
        SELECT
            c.player_id as id,
            c.player_name as name,
            'D' as tier,
            c.elo, c.helo, c.celo, c.gelo,
            c.rank as ranking,
            c.elo_rank,
            COALESCE(
                c.form,
                0.75 * COALESCE(c.form_4w, 0) + 0.25 * COALESCE(c.form_12w, 0),
                0
            ) as form
        FROM tennis.elo_current c
        WHERE c.player_id = :player_id
    """
    
    try:
        result = db.execute(text(sql), {"player_id": player_id})
        row = result.mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Player not found")
        return Player(**dict(row))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{player_id}/elo_history", response_model=PlayerEloHistory)
async def get_player_elo_history(
    player_id: int,
    db: Session = Depends(get_db),
):
    """Get Elo history for a player"""
    cache_key = f"players:elo_history:{player_id}"
    cached = cache_get(cache_key)
    if cached is not None:
        return PlayerEloHistory(**cached)
    # First get player name
    player_sql = "SELECT player_name FROM tennis.elo_current WHERE player_id = :player_id"
    player_result = db.execute(text(player_sql), {"player_id": player_id})
    player_row = player_result.mappings().first()
    if not player_row:
        raise HTTPException(status_code=404, detail="Player not found")
    
    player_name = player_row["player_name"]
    
    sql = """
        SELECT
            s.scraped_at::date as date,
            r.elo, r.helo, r.celo, r.gelo
        FROM tennis.elo_ratings r
        JOIN tennis.elo_snapshots s ON s.id = r.snapshot_id
        WHERE r.player_name = :player_name
        ORDER BY s.scraped_at DESC
        LIMIT 52
    """
    
    try:
        result = db.execute(text(sql), {"player_name": player_name})
        rows = result.mappings().all()
        history = [
            PlayerEloHistoryPoint(
                date=str(row["date"]),
                elo=row["elo"] or 1500,
                helo=row.get("helo"),
                celo=row.get("celo"),
                gelo=row.get("gelo"),
            )
            for row in reversed(rows)
        ]
        payload = PlayerEloHistory(
            player_id=player_id,
            player_name=player_name,
            history=history,
        )
        cache_set(cache_key, payload.model_dump(), ttl=300)
        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

