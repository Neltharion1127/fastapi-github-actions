from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from app.core import redis_client
from app.db import Base, get_engine
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Optional: create tables on startup (for dev/test environments)
    if os.getenv("CREATE_TABLES_ON_STARTUP", "false").lower() == "true":
        engine = get_engine()
        if engine:
            Base.metadata.create_all(bind=engine)
    
    # Note: we no longer ping Redis on startup to allow graceful degradation
    # Use /ready endpoint to check dependency health
    
    yield
    
    # Cleanup on shutdown
    await redis_client.close_redis()


app = FastAPI(lifespan=lifespan)

# Register all endpoints
app.include_router(router)


# CORS for local frontend dev (cookie-based refresh token requires credentials)
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://web.jensending.top"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
