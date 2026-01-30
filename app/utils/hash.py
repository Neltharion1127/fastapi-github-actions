# @Time: 1/29/26 22:35
# @Author: jie
# @File: hash.py
# @Description:
import hashlib
import secrets
import time

REFRESH_TTL_SECONDS = 7 * 24 * 60 * 60

def generate_refresh_token() -> str:
    return secrets.token_urlsafe(32)  # plain token stored in cookie

def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def now_ts() -> int:
    return int(time.time())