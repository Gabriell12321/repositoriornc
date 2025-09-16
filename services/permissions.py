import sqlite3
import logging
from .db import DB_PATH

logger = logging.getLogger('ippel.services.permissions')


def get_user_department(user_id: int) -> str | None:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT department FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        logger.error(f"Erro ao obter departamento: {e}")
        return None


def has_department_permission(user_id: int, action: str) -> bool:
    try:
        dept = (get_user_department(user_id) or '').lower()
        if not dept:
            return False
        if dept in ['administração', 'administracao', 'ti']:
            return True
        if action in {'view_own_rncs', 'edit_rncs', 'view_groups_for_assignment', 'view_users_for_assignment'}:
            return True
        # Permissões amplas (incluem Qualidade)
        if action in {'view_all_rncs', 'view_finalized_rncs', 'view_charts', 'view_levantamento_14_15'}:
            return dept in ['administração', 'administracao', 'ti', 'qualidade']
        # Relatórios e Gastos: Admin/TI/Qualidade
        if action in {'view_reports', 'can_print_reports', 'view_employee_expenses'}:
            return dept in ['administração', 'administracao', 'ti', 'qualidade']
        if action in {'admin_access', 'manage_users'}:
            return dept in ['administração', 'administracao', 'ti']
        return False
    except Exception as e:
        logger.error(f"Erro dept permission: {e}")
        return False


def has_permission(user_id: int, permission: str) -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        if row and row[0] == 'admin':
            conn.close()
            return True
        cursor.execute('''
            SELECT gp.permission_value
              FROM group_permissions gp
              JOIN users u ON u.group_id = gp.group_id
             WHERE u.id = ? AND gp.permission_name = ?
        ''', (user_id, permission))
        res = cursor.fetchone()
        conn.close()
        if res and res[0] == 1:
            return True
        return has_department_permission(user_id, permission)
    except Exception as e:
        logger.error(f"Erro has_permission: {e}")
        return False
