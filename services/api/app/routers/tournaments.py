"""
Tournaments router
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.session import get_db
from app.db.cache import cache_get, cache_set
from app.schemas.tournament import Tournament

router = APIRouter()


@router.get("", response_model=List[Tournament])
async def get_tournaments(
    tour: Optional[str] = Query(None, description="Tour: atp or wta"),
    db: Session = Depends(get_db),
):
    """Get list of tournaments"""
    cache_key = f"tournaments:list:{tour}"
    cached = cache_get(cache_key)
    if cached is not None:
        return [Tournament(**row) for row in cached]

    sql = """
        SELECT
            id, tournament_name as name, tour, season_year, source_url
        FROM tennis.draw_sources
        WHERE active = 1
          AND (:tour IS NULL OR tour = :tour)
        ORDER BY season_year DESC, tournament_name ASC
    """
    
    try:
        result = db.execute(text(sql), {"tour": tour})
        rows = result.mappings().all()
        data = [dict(row) for row in rows]
        cache_set(cache_key, data, ttl=300)
        return [Tournament(**row) for row in data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active", response_model=Optional[Tournament])
async def get_active_tournament(
    tour: str = Query(..., description="Tour: atp or wta"),
    db: Session = Depends(get_db),
):
    """Get the most recent active tournament for a tour"""
    cache_key = f"tournaments:active:{tour}"
    cached = cache_get(cache_key)
    if cached is not None:
        return Tournament(**cached)

    sql = """
        SELECT
            ds.id, ds.tournament_name as name, ds.tour, ds.season_year, ds.source_url
        FROM tennis.draw_sources ds
        JOIN tennis.draw_snapshots snap ON snap.source_id = ds.id
        WHERE ds.active = 1 AND ds.tour = :tour AND snap.status = 'success'
        ORDER BY snap.scraped_at DESC
        LIMIT 1
    """
    
    try:
        result = db.execute(text(sql), {"tour": tour})
        row = result.mappings().first()
        if not row:
            return None
        data = dict(row)
        cache_set(cache_key, data, ttl=120)
        return Tournament(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{tournament_id}", response_model=Tournament)
async def get_tournament(
    tournament_id: int,
    db: Session = Depends(get_db),
):
    """Get single tournament by ID"""
    sql = """
        SELECT
            id, tournament_name as name, tour, season_year, source_url
        FROM tennis.draw_sources
        WHERE id = :tournament_id
    """
    
    try:
        result = db.execute(text(sql), {"tournament_id": tournament_id})
        row = result.mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Tournament not found")
        return Tournament(**dict(row))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


