# @Time: 1/28/26 02:00
# @Author: jie
# @File: deps.py
# @Description: FastAPI dependencies (deps) incl. JWT auth

from __future__ import annotations

from typing import Any, Dict, Optional

import jwt
from fastapi import Header, HTTPException, status

from .jwt import decode_and_verify


def get_bearer_token(authorization: Optional[str]) -> Optional[str]:
    """Extract Bearer token from Authorization header.

    Input examples:
      - "Bearer xxx"
      - None

    Returns:
      - "xxx" or None
    """
    if not authorization:
        return None

    parts = authorization.split(" ")
    if len(parts) != 2:
        return None

    scheme, token = parts[0], parts[1]
    if scheme.lower() != "bearer":
        return None

    token = token.strip()
    return token if token else None


def decode_and_verify_jwt(token: str) -> Dict[str, Any]:
    """Verify JWT and return payload.

    This function translates JWT library errors into FastAPI-friendly HTTP 401.
    """
    try:
        payload = decode_and_verify(token)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    """FastAPI dependency: get current user from Bearer token.

    Usage in routes:
      current_user = Depends(get_current_user)

    For demo purposes, it returns the JWT payload directly.
    """
    token = get_bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_and_verify_jwt(token)

    # Minimal sanity check
    if "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload