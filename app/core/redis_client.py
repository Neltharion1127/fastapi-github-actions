# @Time: 1/30/26 00:22
# @Author: jie
# @File: redis_client.py
# @Description:
import os
import redis

REDIS_URL = os.getenv("REDIS_URL")

if not REDIS_URL:
    raise RuntimeError("REDIS_URL environment variable is not set")

rds = redis.from_url(REDIS_URL, decode_responses=True)


async def ping_redis() -> None:
    """
    Verify Redis connectivity at application startup.

    Called from FastAPI lifespan (startup phase).
    Fail fast if Redis is unreachable or misconfigured.
    """
    rds.ping()


async def close_redis() -> None:
    """
    Gracefully close Redis connections at application shutdown.

    Called from FastAPI lifespan (shutdown phase).
    Safe to call even if Redis was never used.
    """
    rds.close()