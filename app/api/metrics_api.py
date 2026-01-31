import time
from fastapi import APIRouter, Depends

from app.core.deps import get_current_user

metrics_router = APIRouter()

START_TIME = time.time()
REQUEST_COUNT = 0

@metrics_router.get("/")
def read_root():
    return {"message": "This is a sample FastAPI application."}

@metrics_router.get("/health")
def health():
    return {"status": "ok"}

@metrics_router.get("/hello")
def hello(name: str = "world"):
    return {"message": f"hello {name}"}

@metrics_router.get("/metrics")
def metrics(current_user: dict = Depends(get_current_user)):
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    return {
        "uptime_seconds": int(time.time() - START_TIME),
        "request_count": REQUEST_COUNT,
    }


@metrics_router.get("/ready")
async def ready():
    """
    Check all external dependencies for readiness.
    
    Returns 200 if all configured dependencies are healthy.
    Returns 503 if any configured dependency is unhealthy.
    """
    from app.db import check_database_ready
    from app.core.redis_client import check_redis_ready
    
    db_status = check_database_ready()
    redis_status = await check_redis_ready()
    
    status = {**db_status, **redis_status}
    
    # Consider "not_configured" as acceptable (dependency is optional)
    all_ok = all(v == "ok" or v == "not_configured" for v in status.values())
    
    if not all_ok:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=status)
    
    return {"status": "ready", "dependencies": status}

