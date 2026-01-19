"""
Redis cache management
"""
import json
import redis
from typing import Optional, Any
from functools import wraps

from app.core.config import settings

# Redis client
redis_client: Optional[redis.Redis] = None


def get_redis() -> Optional[redis.Redis]:
    """Get Redis client, creating if necessary"""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            redis_client.ping()
        except Exception:
            redis_client = None
    return redis_client


def cache_get(key: str) -> Optional[Any]:
    """Get value from cache"""
    client = get_redis()
    if client is None:
        return None
    try:
        data = client.get(key)
        if data:
            return json.loads(data)
    except Exception:
        pass
    return None


def cache_set(key: str, value: Any, ttl: int = 300) -> bool:
    """Set value in cache with TTL in seconds"""
    client = get_redis()
    if client is None:
        return False
    try:
        client.setex(key, ttl, json.dumps(value))
        return True
    except Exception:
        return False


def cache_delete(key: str) -> bool:
    """Delete value from cache"""
    client = get_redis()
    if client is None:
        return False
    try:
        client.delete(key)
        return True
    except Exception:
        return False


def cached(key_prefix: str, ttl: int = 300):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key from args
            cache_key = f"{key_prefix}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_value = cache_get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Cache result
            cache_set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


