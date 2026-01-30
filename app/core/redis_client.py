import os
import redis.asyncio as redis

"""
Redis client utilities.

Design goals:
- One shared Redis client per process
- Async-compatible with FastAPI lifespan
- Safe in CI / local environments without Redis
- Fail-fast can be enabled explicitly via env
"""


REDIS_URL = os.getenv("REDIS_URL", "")

redis_client = (
    redis.from_url(
        REDIS_URL,
        decode_responses=True,  # return str instead of bytes
    )
    if REDIS_URL
    else None
)

# Alias for backward compatibility
rds = redis_client


async def ping_redis() -> None:
    """
    Verify Redis connectivity at application startup.

    - If REDIS_URL is not set: no-op (useful for CI)
    - If REDIS_URL is set but Redis is unreachable: raises exception
    """
    if redis_client is None:
        # Redis not configured (CI / local without Redis)
        return

    await redis_client.ping()


async def close_redis() -> None:
    """
    Gracefully close Redis connections at application shutdown.

    Safe to call even if Redis was never configured or used.
    """
    if redis_client is None:
        return

    await redis_client.close()