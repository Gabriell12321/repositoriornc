#!/usr/bin/env python3
import sqlite3

def complete_admin_permissions():
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    print("🔧 Completando permissões do admin...")
    
    # 1. Obter grupo Admin
    cursor.execute("SELECT id FROM groups WHERE name = 'Administrador'")
    admin_group_id = cursor.fetchone()[0]
    
    # 2. Lista de todas as permissões necessárias
    all_permissions = [
        'create_rnc', 'update_avatar', 'edit_own_rnc', 'view_own_rnc',
        'view_all_rncs', 'edit_all_rncs', 'delete_rnc', 'reply_rncs',
        'share_rncs', 'finalize_rncs', 'assign_rncs', 'view_finalized_rncs',
        'view_charts', 'view_reports', 'export_data', 'admin_access',
        'manage_users', 'manage_groups', 'view_engineering_rncs',
        'view_all_departments_rncs', 'view_levantamento_14_15',
        'view_groups_for_assignment', 'view_users_for_assignment',
        'view_audit_logs', 'manage_system_settings'
    ]
    
    print(f"✅ Adicionando {len(all_permissions)} permissões...")
    
    # 3. Adicionar todas as permissões
    for permission in all_permissions:
        cursor.execute("INSERT OR REPLACE INTO group_permissions (group_id, permission_name, permission_value) VALUES (?, ?, ?)", 
                       (admin_group_id, permission, 1))
    
    # 4. Commit
    conn.commit()
    
    # 5. Verificar resultado
    cursor.execute("SELECT COUNT(*) FROM group_permissions WHERE group_id = ?", (admin_group_id,))
    total_perms = cursor.fetchone()[0]
    
    print(f"✅ Total de permissões configuradas: {total_perms}")
    print("🎉 Admin agora tem todas as permissões necessárias!")
    
    conn.close()

if __name__ == "__main__":
    complete_admin_permissions()
