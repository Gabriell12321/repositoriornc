import sqlite3
import time
import logging
from .db import DB_PATH

logger = logging.getLogger('ippel.services.rnc')


def share_rnc_with_user(rnc_id: int, shared_by_user_id: int, shared_with_user_id: int, permission_level: str = 'view') -> bool:
    attempt = 0
    max_attempts = 10  # Aumentando número de tentativas
    backoff_base = 0.5  # Backoff mais longo
    while attempt < max_attempts:
        conn = None
        try:
            # Aumentando timeout e usando conexão da pool
            try:
                from .db import get_db_connection, return_db_connection
                conn = get_db_connection()  # Usar conexão da pool com configurações otimizadas
            except Exception:
                # Fallback se falhar importação ou pool
                conn = sqlite3.connect(DB_PATH, timeout=30.0, isolation_level=None)
                cursor = conn.cursor()
                cursor.execute('PRAGMA busy_timeout=15000')  # 15 segundos de espera
            
            cursor = conn.cursor()
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
    """Determina acesso de visualização a uma RNC.
    Regras:
    - Admin: sempre pode
    - Criador: pode
    - Responsável atribuído (assigned_user_id): pode
    - Compartilhado em rnc_shares: pode
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Admin tem acesso total
        cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        role_row = cursor.fetchone()
        if role_row and str(role_row[0]).lower() == 'admin':
            conn.close()
            return True

        # Verificar criador e responsável atribuído
        cursor.execute('SELECT user_id, assigned_user_id FROM rncs WHERE id = ?', (rnc_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return False
        owner_id, assigned_id = row[0], row[1]
        if str(owner_id) == str(user_id) or (assigned_id is not None and str(assigned_id) == str(user_id)):
            conn.close()
            return True

        # Verificar compartilhamento explícito
        cursor.execute('''
            SELECT 1 FROM rnc_shares WHERE rnc_id = ? AND shared_with_user_id = ? LIMIT 1
        ''', (rnc_id, user_id))
        shared = cursor.fetchone() is not None
        conn.close()
        return shared
    except Exception as e:
        logger.error(f"Erro em can_user_access_rnc: {e}")
        return False
