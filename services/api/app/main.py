"""
Tournament Studio API - FastAPI Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
import logging

from app.core.config import settings
from app.routers import players, tournaments, matchups, draws, simulations, scorito
from app.db.session import engine

app = FastAPI(
    title="Tournament Studio API",
    description="Backend API for Tennis Tournament Analytics and Simulation",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Must be False when using "*" origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

logger = logging.getLogger("api")

@app.on_event("startup")
async def ensure_indexes():
    """Create helpful indexes if they don't exist (safe on startup)."""
    statements = [
        "CREATE INDEX IF NOT EXISTS idx_elo_current_gender_name ON tennis.elo_current (gender, player_name)",
        "CREATE INDEX IF NOT EXISTS idx_elo_current_gender_rank ON tennis.elo_current (gender, elo_rank)",
        "CREATE INDEX IF NOT EXISTS idx_elo_snapshots_gender_scraped_at ON tennis.elo_snapshots (gender, scraped_at)",
        "CREATE INDEX IF NOT EXISTS idx_elo_ratings_player_snapshot ON tennis.elo_ratings (player_name, snapshot_id)",
    ]
    try:
        with engine.begin() as conn:
            for stmt in statements:
                conn.execute(text(stmt))
    except Exception as exc:
        logger.warning("Index creation skipped: %s", exc)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


# Include routers
app.include_router(players.router, prefix="/api/v1/players", tags=["players"])
app.include_router(tournaments.router, prefix="/api/v1/tournaments", tags=["tournaments"])
app.include_router(matchups.router, prefix="/api/v1/matchups", tags=["matchups"])
app.include_router(draws.router, prefix="/api/v1/draws", tags=["draws"])
app.include_router(simulations.router, prefix="/api/v1/simulations", tags=["simulations"])
app.include_router(scorito.router, prefix="/api/v1/scorito", tags=["scorito"])


# Predictions endpoints (combined)
@app.get("/api/v1/predictions/summary")
async def get_predictions_summary(tournament_id: int):
    """Get prediction summary for tournament"""
    # Placeholder - will be implemented with actual simulation
    return {
        "finalists": [],
        "semifinalists": [],
        "quarterfinalists": [],
    }


@app.get("/api/v1/predictions/top_picks")
async def get_top_picks(tournament_id: int):
    """Get top picks for tournament"""
    return []


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

