"""
JWT authentication utilities: access and refresh tokens with rotation and revocation.

Design:
- Uses HS256 with secret from env JWT_SECRET (fallback to ippel_secret.key or Flask secret).
- Access token: short-lived (default 15 minutes), carries user identity claims.
- Refresh token: longer-lived (default 7 days), stored in SQLite table refresh_tokens by jti and revocable.
- Rotation: on refresh, revoke old refresh token and issue a new pair.

Note: This module avoids importing the Flask app. It relies on environment or local key file for secret.
"""
from __future__ import annotations

import os
import time
import uuid
import sqlite3
from typing import Any, Dict, Optional, Tuple

import jwt  # PyJWT

from services.db import DB_PATH


ALGORITHM = "HS256"
DEFAULT_ACCESS_TTL = int(os.environ.get("JWT_ACCESS_TTL_SECONDS", "900"))  # 15 min
DEFAULT_REFRESH_TTL = int(os.environ.get("JWT_REFRESH_TTL_SECONDS", str(7 * 24 * 3600)))  # 7 days


def _load_fallback_secret() -> str:
    # Try env first
    env = os.environ.get("JWT_SECRET")
    if env:
        return env
    # Fallback to ippel_secret.key in repo root (same as server_form.py uses)
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        key_path = os.path.join(base_dir, "ippel_secret.key")
        if os.path.exists(key_path):
            with open(key_path, "r", encoding="utf-8") as f:
                return f.read().strip()
    except Exception:
        pass
    # Final fallback: ephemeral
    return os.environ.get("FLASK_SECRET_FALLBACK", "dev-secret-change-me")


def get_secret() -> str:
    return _load_fallback_secret()


def _ensure_tables() -> None:
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jti TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                expires_at INTEGER NOT NULL,
                revoked INTEGER DEFAULT 0,
                created_at INTEGER DEFAULT (strftime('%s','now')),
                user_agent TEXT,
                ip TEXT
            )
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires ON refresh_tokens(expires_at)")
        conn.commit()
        conn.close()
    except Exception:
        pass


def _store_refresh_token(jti: str, user_id: int, expires_at: int, user_agent: Optional[str], ip: Optional[str]) -> None:
    _ensure_tables()
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO refresh_tokens (jti, user_id, expires_at, revoked, user_agent, ip) VALUES (?, ?, ?, COALESCE((SELECT revoked FROM refresh_tokens WHERE jti = ?), 0), ?, ?)",
            (jti, user_id, expires_at, jti, user_agent, ip),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def _revoke_refresh_token(jti: str) -> None:
    _ensure_tables()
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("UPDATE refresh_tokens SET revoked = 1 WHERE jti = ?", (jti,))
        conn.commit()
        conn.close()
    except Exception:
        pass


def _is_refresh_revoked(jti: str) -> bool:
    _ensure_tables()
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT revoked, expires_at FROM refresh_tokens WHERE jti = ?", (jti,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return True  # unknown = treat as revoked
        revoked, expires_at = row
        if int(time.time()) >= int(expires_at):
            return True
        return bool(revoked)
    except Exception:
        return True


def _build_claims(user_row: tuple) -> Dict[str, Any]:
    # users schema: id, name, email, password_hash, department, role, ...
    return {
        "sub": int(user_row[0]),
        "name": user_row[1],
        "email": user_row[2],
        "department": user_row[4],
        "role": user_row[5],
    }


def create_access_token(user_row: tuple, ttl_seconds: Optional[int] = None) -> Tuple[str, int]:
    secret = get_secret()
    now = int(time.time())
    ttl = int(ttl_seconds or DEFAULT_ACCESS_TTL)
    claims = _build_claims(user_row)
    payload = {
        **claims,
        "iat": now,
        "nbf": now,
        "exp": now + ttl,
        "type": "access",
    }
    token = jwt.encode(payload, secret, algorithm=ALGORITHM)
    return token, payload["exp"]


def create_refresh_token(user_row: tuple, ttl_seconds: Optional[int] = None, user_agent: Optional[str] = None, ip: Optional[str] = None) -> Tuple[str, int, str]:
    secret = get_secret()
    now = int(time.time())
    ttl = int(ttl_seconds or DEFAULT_REFRESH_TTL)
    jti = uuid.uuid4().hex
    claims = {
        "sub": int(user_row[0]),
        "iat": now,
        "nbf": now,
        "exp": now + ttl,
        "type": "refresh",
        "jti": jti,
    }
    token = jwt.encode(claims, secret, algorithm=ALGORITHM)
    _store_refresh_token(jti, int(user_row[0]), claims["exp"], user_agent, ip)
    return token, claims["exp"], jti


class JWTError(Exception):
    pass


def decode_token(token: str, verify_type: Optional[str] = None) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, get_secret(), algorithms=[ALGORITHM])
        if verify_type and payload.get("type") != verify_type:
            raise JWTError("invalid_token_type")
        return payload
    except jwt.ExpiredSignatureError as e:
        raise JWTError("token_expired") from e
    except jwt.InvalidTokenError as e:
        raise JWTError("invalid_token") from e


def rotate_refresh(old_refresh_token: str, user_agent: Optional[str], ip: Optional[str], user_row_provider) -> Tuple[str, int, str, str, int]:
    """
    Verify old refresh token, revoke it, re-issue new refresh and a fresh access.
    user_row_provider: callable(user_id:int)->tuple to rehydrate user for claims
    Returns: (new_access, access_exp, new_refresh, refresh_exp, user_id)
    """
    payload = decode_token(old_refresh_token, verify_type="refresh")
    jti = payload.get("jti")
    if not jti or _is_refresh_revoked(jti):
        raise JWTError("refresh_revoked")
    uid = int(payload.get("sub"))
    # revoke old
    _revoke_refresh_token(jti)
    # reissue
    user_row = user_row_provider(uid)
    if not user_row:
        raise JWTError("user_not_found")
    access, access_exp = create_access_token(user_row)
    new_refresh, refresh_exp, _new_jti = create_refresh_token(user_row, user_agent=user_agent, ip=ip)
    return access, access_exp, new_refresh, refresh_exp, uid


def revoke_refresh(jti: str) -> None:
    _revoke_refresh_token(jti)
