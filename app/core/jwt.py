# @Time: 1/28/26 02:00
# @Author: jie
# @File: jwt.py
# @Description: Minimal JWT helpers for demo (Bearer Token)

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import os
import jwt

# ===== Config (for demo) =====
# In a real project, read these from env / settings.
JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 *24


def create_access_token(
    subject: str,
    *,
    expires_delta: Optional[timedelta] = None,
    claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a JWT access token.

    - subject: usually user id / email
    - claims: extra fields to embed in payload
    """
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    payload: Dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    if claims:
        # Avoid overwriting standard claims accidentally
        for k, v in claims.items():
            if k in payload:
                continue
            payload[k] = v

    token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)
    # PyJWT may return str in modern versions; keep it as str
    return token


def decode_and_verify(token: str) -> Dict[str, Any]:
    """Decode and verify JWT.

    Raises:
      - jwt.ExpiredSignatureError
      - jwt.InvalidTokenError
    """
    payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    # Ensure it is a dict
    return dict(payload)
