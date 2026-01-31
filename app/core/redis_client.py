import os
from functools import lru_cache
from typing import Optional

import redis.asyncio as redis

"""
Redis client utilities with lazy initialization.

Design goals:
- Lazy loading: client created on first use, not at import time
- One shared Redis client per process (singleton via lru_cache)
- Async-compatible with FastAPI lifespan
- Safe in CI / local environments without Redis
- Health check support via check_redis_ready()
"""


@lru_cache(maxsize=1)
def get_redis_client() -> Optional[redis.Redis]:
    """
    Lazily create and return the Redis client singleton.

    Returns None if REDIS_URL is not configured.
    The client is created on first call and cached for subsequent calls.
    """
    url = os.getenv("REDIS_URL", "")
    if not url:
        return None
    return redis.from_url(url, decode_responses=True)


# Alias for backward compatibility and convenience
def rds() -> Optional[redis.Redis]:
    """Convenience alias for get_redis_client()."""
    return get_redis_client()


async def check_redis_ready() -> dict:
    """
    Check Redis connectivity for /ready endpoint.

    Returns:
        {"redis": "ok"} if connected
        {"redis": "not_configured"} if REDIS_URL not set
        {"redis": "error: <message>"} if connection failed
    """
    client = get_redis_client()
    if client is None:
        return {"redis": "not_configured"}
    try:
        await client.ping()
        return {"redis": "ok"}
    except Exception as e:
        return {"redis": f"error: {str(e)}"}


async def ping_redis() -> None:
    """
    Verify Redis connectivity at application startup (optional).

    - If REDIS_URL is not set: no-op (useful for CI)
    - If REDIS_URL is set but Redis is unreachable: raises exception
    """
    client = get_redis_client()
    if client is None:
        return
    await client.ping()


async def close_redis() -> None:
    """
    Gracefully close Redis connections at application shutdown.

    Safe to call even if Redis was never configured or used.
    """
    client = get_redis_client()
    if client is None:
        return
    await client.close()