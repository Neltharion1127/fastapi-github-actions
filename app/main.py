import time
from fastapi import FastAPI, Request

START_TIME = time.time()
REQUEST_COUNT = 0

app = FastAPI()

@app.middleware("http")
async def count_requests(request: Request, call_next):
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    return await call_next(request)

@app.get("/")
def read_root():
    return {"message": "This is a sample FastAPI application."}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/hello")
def hello(name: str = "world"):
    return {"message": f"hello {name}"}

@app.get("/metrics")
def metrics():
    return {
        "uptime_seconds": int(time.time() - START_TIME),
        "request_count": REQUEST_COUNT,
    }