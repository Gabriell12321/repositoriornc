"""
Progressive account lockout service for authentication hardening.

Schema: login_lockouts (per-user)
- user_id INTEGER PRIMARY KEY
- failed_count INTEGER NOT NULL DEFAULT 0
- last_failed_at INTEGER (epoch seconds)
- locked_until INTEGER (epoch seconds)
- last_ip TEXT

Behavior:
- On failed login, increment failed_count and, at thresholds (>=5, >=10, >=15), set locked_until
  to 15m, 1h, 24h respectively from now. Existing active locks are respected.
- On successful login, reset failed_count to 0 and clear locked_until.
- is_locked(user_id) returns (True, seconds_remaining) if locked.
"""
from __future__ import annotations

import sqlite3
import time
from typing import Optional, Tuple

DB_PATH = 'ippel_system.db'


def _conn():
    return sqlite3.connect(DB_PATH)


def ensure_table() -> None:
    try:
        conn = _conn(); cur = conn.cursor()
        cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS login_lockouts (
                user_id INTEGER PRIMARY KEY,
                failed_count INTEGER NOT NULL DEFAULT 0,
                last_failed_at INTEGER,
                locked_until INTEGER,
                last_ip TEXT
            )
            '''
        )
        conn.commit(); conn.close()
    except Exception:
        try: conn.close()
        except Exception: pass


def get_record(user_id: int) -> Optional[Tuple[int, int, int, int, Optional[str]]]:
    ensure_table()
    conn = None
    try:
        conn = _conn(); cur = conn.cursor()
        cur.execute('SELECT user_id, failed_count, last_failed_at, locked_until, last_ip FROM login_lockouts WHERE user_id = ?', (user_id,))
        row = cur.fetchone(); conn.close()
        return row
    except Exception:
        try: conn.close()
        except Exception: pass
        return None


def is_locked(user_id: int) -> Tuple[bool, int]:
    """Return (locked, seconds_remaining)."""
    rec = get_record(user_id)
    if not rec:
        return False, 0
    _uid, _count, _last_failed, locked_until, _ip = rec
    if not locked_until:
        return False, 0
    now = int(time.time())
    if locked_until > now:
        return True, locked_until - now
    return False, 0


def reset_success(user_id: int) -> None:
    ensure_table()
    conn = None
    try:
        conn = _conn(); cur = conn.cursor()
        cur.execute(
            'INSERT INTO login_lockouts (user_id, failed_count, last_failed_at, locked_until, last_ip) VALUES (?, 0, NULL, NULL, NULL) '
            'ON CONFLICT(user_id) DO UPDATE SET failed_count = 0, last_failed_at = NULL, locked_until = NULL'
            , (user_id,)
        )
        conn.commit(); conn.close()
    except Exception:
        try: conn.close()
        except Exception: pass


def record_failure(user_id: int, ip: Optional[str] = None) -> Tuple[int, Optional[int]]:
    """Increment failure count and set lock if thresholds reached.
    Returns (failed_count, locked_until_epoch_or_None).
    """
    ensure_table()
    now = int(time.time())
    conn = None
    try:
        conn = _conn(); cur = conn.cursor()
        cur.execute('SELECT failed_count, locked_until FROM login_lockouts WHERE user_id = ?', (user_id,))
        row = cur.fetchone()
        if not row:
            failed = 1
            locked_until = None
            cur.execute('INSERT INTO login_lockouts (user_id, failed_count, last_failed_at, locked_until, last_ip) VALUES (?, ?, ?, ?, ?)',
                        (user_id, failed, now, None, ip))
        else:
            failed = (row[0] or 0) + 1
            locked_until = row[1]
            # If currently locked, keep existing lock
            # Else set new lock at thresholds
            if not locked_until:
                if failed >= 15:
                    locked_until = now + 24*3600
                elif failed >= 10:
                    locked_until = now + 60*60
                elif failed >= 5:
                    locked_until = now + 15*60
            cur.execute('UPDATE login_lockouts SET failed_count = ?, last_failed_at = ?, locked_until = ?, last_ip = ? WHERE user_id = ?',
                        (failed, now, locked_until, ip, user_id))
        conn.commit(); conn.close()
        return failed, locked_until
    except Exception:
        try: conn.close()
        except Exception: pass
        return 0, None
