import sqlite3
from typing import Optional, Tuple

DB_PATH = 'ippel_system.db'

# Returns (id, name, email, password_hash, department, role)
def get_user_by_email(email: str) -> Optional[Tuple[int, str, str, str, str, str]]:
    if not email:
        return None
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # CORRIGIDO: Verificar se o usuário está ativo (is_active = 1)
        cursor.execute('SELECT id, name, email, password_hash, department, role FROM users WHERE email = ? AND is_active = 1', (email,))
        row = cursor.fetchone()
        return row
    except Exception:
        return None
    finally:
        try:
            if conn:
                conn.close()
        except Exception:
            pass
