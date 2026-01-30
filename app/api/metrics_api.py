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
