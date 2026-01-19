"""
Configuration settings for the API
"""
from typing import List
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    # Connect to the existing tennis_dagster_postgres database with actual data
    DATABASE_URL: str = "postgresql://tennis:tennis@tennis_dagster_postgres:5432/tennis_simulator"
    
    # Redis
    # Port 6380 to avoid conflict with nba_stats_redis on 6379
    REDIS_URL: str = "redis://localhost:6380/0"
    
    # CORS
    # Allow all origins for development (use specific origins in production)
    CORS_ORIGINS: List[str] = ["*"]
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # Simulation defaults
    DEFAULT_NUM_SIMULATIONS: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

