import sqlite3
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from .db import DB_PATH, get_db_connection, return_db_connection

logger = logging.getLogger('ippel.services.groups')

# Simple TTL cache for read-heavy endpoints
_CACHE_TTL_SECONDS = 30.0
_cache: Dict[Tuple[Any, ...], Tuple[float, Any]] = {}


def _cache_get(key: Tuple[Any, ...]):
    now = time.time()
    item = _cache.get(key)
    if not item:
        return None
    ts, value = item
    if now - ts > _CACHE_TTL_SECONDS:
        _cache.pop(key, None)
        return None
    return value


def _cache_set(key: Tuple[Any, ...], value: Any) -> None:
    _cache[key] = (time.time(), value)


def _cache_invalidate(*prefixes: Tuple[Any, ...]) -> None:
    if not prefixes:
        _cache.clear()
        return
    keys = list(_cache.keys())
    for k in keys:
        for p in prefixes:
            if k[: len(p)] == p:
                _cache.pop(k, None)
                break


def get_all_groups() -> List[tuple]:
    cache_key = ("all_groups",)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT g.id, g.name, g.description, COUNT(u.id) as user_count
              FROM groups g
              LEFT JOIN users u ON g.id = u.group_id AND u.is_active = 1
             GROUP BY g.id
             ORDER BY lower(g.name)
            '''
        )
        rows = cursor.fetchall()
        _cache_set(cache_key, rows)
        return rows
    except Exception as e:
        logger.error(f"Erro ao buscar grupos: {e}")
        return []
    finally:
        if conn:
            return_db_connection(conn)


def get_group_by_id(group_id: int) -> Optional[tuple]:
    # validação básica
    if not isinstance(group_id, int) or group_id <= 0:
        logger.warning("get_group_by_id: group_id inválido: %r", group_id)
        return None
    cache_key = ("group_by_id", group_id)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM groups WHERE id = ?', (group_id,))
        row = cursor.fetchone()
        _cache_set(cache_key, row)
        return row
    except Exception as e:
        logger.error(f"Erro ao buscar grupo: {e}")
        return None
    finally:
        if conn:
            return_db_connection(conn)


def get_users_by_group(group_id: int) -> List[tuple]:
    if not isinstance(group_id, int) or group_id <= 0:
        logger.warning("get_users_by_group: group_id inválido: %r", group_id)
        return []
    cache_key = ("users_by_group", group_id)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT id, name, email, department, role, is_active
              FROM users
             WHERE group_id = ? AND is_active = 1
             ORDER BY lower(name)
            ''',
            (group_id,),
        )
        rows = cursor.fetchall()
        _cache_set(cache_key, rows)
        return rows
    except Exception as e:
        logger.error(f"Erro ao buscar usuários do grupo: {e}")
        return []
    finally:
        if conn:
            return_db_connection(conn)


def create_group(name: str, description: str) -> Optional[int]:
    # validações
    if not isinstance(name, str) or not name.strip():
        logger.warning("create_group: nome inválido")
        return None
    name = name.strip()
    if len(name) > 120:
        logger.warning("create_group: nome muito longo, truncando para 120 chars")
        name = name[:120]
    if not isinstance(description, str):
        description = ""
    description = description.strip()
    if len(description) > 500:
        description = description[:500]

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO groups (name, description) VALUES (?, ?)', (name, description))
        gid = cursor.lastrowid
        conn.commit()
        # invalidar caches relacionados
        _cache_invalidate(("all_groups",), ("group_by_id",), ("users_by_group",))
        return gid
    except sqlite3.IntegrityError as e:
        logger.error(f"Erro de integridade ao criar grupo: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        return None
    except Exception as e:
        logger.error(f"Erro ao criar grupo: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        return None
    finally:
        if conn:
            return_db_connection(conn)


def update_group(group_id: int, name: str, description: str) -> bool:
    if not isinstance(group_id, int) or group_id <= 0:
        logger.warning("update_group: group_id inválido: %r", group_id)
        return False
    if not isinstance(name, str) or not name.strip():
        logger.warning("update_group: nome inválido")
        return False
    name = name.strip()
    if len(name) > 120:
        name = name[:120]
    if not isinstance(description, str):
        description = ""
    description = description.strip()
    if len(description) > 500:
        description = description[:500]

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE groups SET name = ?, description = ? WHERE id = ?', (name, description, group_id))
        conn.commit()
        _cache_invalidate(("all_groups",), ("group_by_id", group_id), ("users_by_group", group_id))
        return True
    except Exception as e:
        logger.error(f"Erro ao atualizar grupo: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        return False
    finally:
        if conn:
            return_db_connection(conn)


def delete_group(group_id: int) -> bool:
    if not isinstance(group_id, int) or group_id <= 0:
        logger.warning("delete_group: group_id inválido: %r", group_id)
        return False
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET group_id = NULL WHERE group_id = ?', (group_id,))
        cursor.execute('DELETE FROM groups WHERE id = ?', (group_id,))
        conn.commit()
        _cache_invalidate(("all_groups",), ("group_by_id", group_id), ("users_by_group", group_id))
        return True
    except Exception as e:
        logger.error(f"Erro ao deletar grupo: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        return False
    finally:
        if conn:
            return_db_connection(conn)
