import sqlite3
import time
import logging
from .db import DB_PATH

logger = logging.getLogger('ippel.services.rnc')


def share_rnc_with_user(rnc_id: int, shared_by_user_id: int, shared_with_user_id: int, permission_level: str = 'view') -> bool:
    attempt = 0
    max_attempts = 5
    backoff_base = 0.2
    while attempt < max_attempts:
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH, timeout=10, isolation_level=None)
            cursor = conn.cursor()
            cursor.execute('PRAGMA busy_timeout=5000')
            cursor.execute('BEGIN IMMEDIATE')
            cursor.execute(
                '''INSERT OR REPLACE INTO rnc_shares (rnc_id, shared_by_user_id, shared_with_user_id, permission_level)
                   VALUES (?, ?, ?, ?)''',
                (rnc_id, shared_by_user_id, shared_with_user_id, permission_level)
            )
            conn.commit()
            return True
        except sqlite3.OperationalError as e:
            msg = str(e).lower()
            if 'locked' in msg or 'busy' in msg:
                attempt += 1
                time.sleep(backoff_base * attempt)
                continue
            else:
                logger.error(f"Erro operacional ao compartilhar RNC {rnc_id}: {e}")
                return False
        except Exception as e:
            logger.error(f"Erro inesperado ao compartilhar RNC {rnc_id}: {e}")
            return False
        finally:
            try:
                if conn:
                    conn.close()
            except Exception:
                pass
    logger.warning("share_rnc_with_user: desistindo após múltiplas tentativas (database locked)")
    return False


def get_rnc_shared_users(rnc_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT rs.shared_with_user_id, rs.permission_level, u.name, u.email
              FROM rnc_shares rs
              JOIN users u ON rs.shared_with_user_id = u.id
             WHERE rs.rnc_id = ?
        ''', (rnc_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"Erro ao buscar usuários compartilhados da RNC {rnc_id}: {e}")
        return []


def can_user_access_rnc(user_id: int, rnc_id: int) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM rncs WHERE id = ?', (rnc_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False
        is_creator = str(row[0]) == str(user_id)
        if is_creator:
            conn.close()
            return True
        cursor.execute('''
            SELECT 1 FROM rnc_shares WHERE rnc_id = ? AND shared_with_user_id = ? LIMIT 1
        ''', (rnc_id, user_id))
        shared = cursor.fetchone() is not None
        conn.close()
        return shared
    except Exception as e:
        logger.error(f"Erro em can_user_access_rnc: {e}")
        return False
