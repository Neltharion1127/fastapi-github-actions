# @Time: 1/28/26 02:40
# @Author: jie
# @File: user_api.py
# @Description:
import hashlib
import secrets
import os

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.core.redis_client import get_redis_client
from app.core.security import PasswordService
from app.db.database import get_db
from app.core.jwt import create_access_token
from app.model import User
from app.model.LoginRequest import LoginRequest
from app.model.RefreshSession import RefreshSession
from app.model.RegisterRequest import RegisterRequest

user_router = APIRouter()

REFRESH_TTL_SECONDS = 7 * 24 * 60 * 60  # 7 days

# Refresh token cookie settings
REFRESH_COOKIE_NAME = "refresh_token"

secure = os.getenv("REFRESH_COOKIE_SECURE") == "true"
samesite = os.getenv("REFRESH_COOKIE_SAMESITE", "lax")


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=secure,
        samesite=samesite,
        max_age=REFRESH_TTL_SECONDS,
        path="/",
    )


@user_router.post("/register")
def register(data: RegisterRequest, db=Depends(get_db)):
    """Register a new user."""
    username = data.username.strip()
    password = data.password
    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(400, "password too long (max 72 bytes for bcrypt)")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    exists = db.query(User).filter(User.username == username).first()
    if exists:
        raise HTTPException(status_code=409, detail="Username already exists")
    u = User(
        username=username,
        password_hash=PasswordService.hash_password(password),
        is_active=True
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return {"message": "registered", "username": username}


@user_router.post("/login")
async def login(data: LoginRequest, response: Response, db=Depends(get_db)):
    """Login: return a short-lived access token; refresh the token stored in HttpOnly cookie."""
    user = db.query(User).filter(User.username == data.username.strip()).first()
    if not user or not PasswordService.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    access_token = create_access_token(user.username)
    plain = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(plain.encode()).hexdigest()

    expires_at = datetime.now(timezone.utc) + timedelta(seconds=REFRESH_TTL_SECONDS)

    session = RefreshSession(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
        revoked_at=None,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Async Redis call
    rds = get_redis_client()
    if rds:
        await rds.setex(
            f"rt:{token_hash}",
            REFRESH_TTL_SECONDS,
            str(session.id)
        )

    _set_refresh_cookie(response, plain)
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@user_router.post("/refresh")
async def refresh(request: Request, response: Response, db=Depends(get_db)):
    """Refresh rotation using HttpOnly cookie.

    Reads refresh token from cookie, rotates it, returns new access token.
    """
    old_plain = request.cookies.get(REFRESH_COOKIE_NAME)
    if not old_plain:
        raise HTTPException(status_code=401, detail="Missing refresh token cookie")

    now = datetime.now(timezone.utc)
    old_hash = hashlib.sha256(old_plain.encode()).hexdigest()
    old_key = f"rt:{old_hash}"

    session = None

    # 1) Try Redis lookup first
    rds = get_redis_client()
    if rds:
        sid = await rds.get(old_key)
        if sid is not None:
            session = db.query(RefreshSession).filter(RefreshSession.id == int(sid)).first()

    # 2) Fallback: DB lookup by token_hash (handles Redis restart / TTL loss)
    if session is None:
        session = db.query(RefreshSession).filter(RefreshSession.token_hash == old_hash).first()

        if session is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        if session.revoked_at is not None:
            raise HTTPException(status_code=401, detail="Refresh token revoked")

        if session.expires_at <= now:
            raise HTTPException(status_code=401, detail="Refresh token expired")

        # Re-hydrate Redis with remaining TTL
        rds_client = get_redis_client()
        if rds_client:
            remaining = int((session.expires_at - now).total_seconds())
            if remaining > 0:
                await rds_client.setex(old_key, remaining, str(session.id))

    # 3) Validate session state (for redis-hit case)
    if session.revoked_at is not None:
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    if session.expires_at <= now:
        # best-effort cleanup
        rds_cleanup = get_redis_client()
        if rds_cleanup:
            await rds_cleanup.delete(old_key)
        raise HTTPException(status_code=401, detail="Refresh token expired")

    # 4) Rotation: revoke old session + delete old redis key
    session.revoked_at = now
    db.commit()
    if rds:
        await rds.delete(old_key)

    # 5) Issue new refresh token (plain in cookie; hash in DB/Redis)
    new_plain = secrets.token_urlsafe(32)
    new_hash = hashlib.sha256(new_plain.encode()).hexdigest()

    new_expires_at = now + timedelta(seconds=REFRESH_TTL_SECONDS)
    new_session = RefreshSession(
        user_id=session.user_id,
        token_hash=new_hash,
        expires_at=new_expires_at,
        revoked_at=None,
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    if rds:
        await rds.setex(f"rt:{new_hash}", REFRESH_TTL_SECONDS, str(new_session.id))

    _set_refresh_cookie(response, new_plain)

    # 6) Return new access token
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not available")

    access_token = create_access_token(user.username)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@user_router.post("/logout")
async def logout(request: Request, response: Response, db=Depends(get_db)):
    """Logout by revoking refresh token.

    - Server: revoke session in DB and delete Redis cache
    - Client: cookie is cleared; access token (JWT) should also be deleted client-side
    """
    token_plain = request.cookies.get(REFRESH_COOKIE_NAME)

    if token_plain:
        token_hash = hashlib.sha256(token_plain.encode()).hexdigest()
        redis_key = f"rt:{token_hash}"

        # Revoke session in DB
        session = db.query(RefreshSession).filter(RefreshSession.token_hash == token_hash).first()
        if session and session.revoked_at is None:
            session.revoked_at = datetime.now(timezone.utc)
            db.commit()

        # Delete from Redis
        rds = get_redis_client()
        if rds:
            await rds.delete(redis_key)

    response.delete_cookie(key=REFRESH_COOKIE_NAME, path="/")
    return {"message": "logged out"}
