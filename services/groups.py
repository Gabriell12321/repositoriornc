import sqlite3
import logging
from .db import DB_PATH

logger = logging.getLogger('ippel.services.groups')


def get_all_groups():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT g.id, g.name, g.description, COUNT(u.id) as user_count
              FROM groups g
              LEFT JOIN users u ON g.id = u.group_id AND u.is_active = 1
             GROUP BY g.id
             ORDER BY g.name
        ''')
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"Erro ao buscar grupos: {e}")
        return []


def get_group_by_id(group_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM groups WHERE id = ?', (group_id,))
        row = cursor.fetchone()
        conn.close()
        return row
    except Exception as e:
        logger.error(f"Erro ao buscar grupo: {e}")
        return None


def get_users_by_group(group_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, email, department, role, is_active
              FROM users
             WHERE group_id = ? AND is_active = 1
             ORDER BY name
        ''', (group_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        logger.error(f"Erro ao buscar usuários do grupo: {e}")
        return []


def create_group(name: str, description: str) -> int | None:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO groups (name, description) VALUES (?, ?)', (name, description))
        gid = cursor.lastrowid
        conn.commit()
        conn.close()
        return gid
    except Exception as e:
        logger.error(f"Erro ao criar grupo: {e}")
        return None


def update_group(group_id: int, name: str, description: str) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE groups SET name = ?, description = ? WHERE id = ?', (name, description, group_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erro ao atualizar grupo: {e}")
        return False


def delete_group(group_id: int) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET group_id = NULL WHERE group_id = ?', (group_id,))
        cursor.execute('DELETE FROM groups WHERE id = ?', (group_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erro ao deletar grupo: {e}")
        return False
