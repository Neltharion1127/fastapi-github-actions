# @Time: 1/29/26 19:13
# @Author: jie
# @File: database.py
# @Description: Database utilities with lazy initialization
import os
from functools import lru_cache
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import Engine


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all models."""
    pass


@lru_cache(maxsize=1)
def get_engine() -> Optional[Engine]:
    """
    Lazily create and return the SQLAlchemy engine singleton.

    Returns None if DATABASE_URL is not configured.
    The engine is created on first call and cached for subsequent calls.
    """
    url = os.getenv("DATABASE_URL", "")
    if not url:
        return None
    return create_engine(url)


@lru_cache(maxsize=1)
def get_session_local() -> Optional[sessionmaker]:
    """
    Lazily create and return the session factory singleton.

    Returns None if DATABASE_URL is not configured.
    """
    engine = get_engine()
    if engine is None:
        return None
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    FastAPI dependency: yield a database session.

    Raises RuntimeError if DATABASE_URL is not configured.
    """
    session_local = get_session_local()
    if session_local is None:
        raise RuntimeError("Database not configured: DATABASE_URL is empty")
    db = session_local()
    try:
        yield db
    finally:
        db.close()


def check_database_ready() -> dict:
    """
    Check database connectivity for /ready endpoint.

    Returns:
        {"database": "ok"} if connected
        {"database": "not_configured"} if DATABASE_URL not set
        {"database": "error: <message>"} if connection failed
    """
    engine = get_engine()
    if engine is None:
        return {"database": "not_configured"}
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"database": "ok"}
    except Exception as e:
        return {"database": f"error: {str(e)}"}


# Backward compatibility aliases
engine = None  # Deprecated: use get_engine()
SessionLocal = None  # Deprecated: use get_session_local()