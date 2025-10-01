#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir permissões do admin diretamente
"""

import sqlite3

def fix_admin_permissions():
    """Corrige as permissões do admin diretamente"""
    
    try:
        print("🔧 Corrigindo permissões do admin...")
        
        # Conectar ao banco
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # 1. Verificar se existe grupo Admin
        print("✅ Verificando grupo Admin...")
        cursor.execute("SELECT id FROM groups WHERE name LIKE '%admin%' OR name LIKE '%Admin%'")
        admin_group = cursor.fetchone()
        
        if not admin_group:
            print("❌ Grupo Admin não encontrado! Criando...")
            cursor.execute("INSERT INTO groups (name, description) VALUES (?, ?)", 
                         ('Administrador', 'Grupo com todas as permissões do sistema'))
            admin_group_id = cursor.lastrowid
            print(f"✅ Grupo Admin criado com ID: {admin_group_id}")
        else:
            admin_group_id = admin_group[0]
            print(f"✅ Grupo Admin encontrado com ID: {admin_group_id}")
        
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
        
        print(f"✅ Total de permissões: {len(all_permissions)}")
        
        # 3. Limpar permissões existentes do grupo Admin
        print("🧹 Limpando permissões existentes...")
        cursor.execute('DELETE FROM group_permissions WHERE group_id = ?', (admin_group_id,))
        
        # 4. Adicionar todas as permissões para o grupo Admin
        print("🔑 Adicionando todas as permissões...")
        for permission in all_permissions:
            cursor.execute('''
                INSERT INTO group_permissions (group_id, permission_name, permission_value)
                VALUES (?, ?, 1)
            ''', (admin_group_id, permission))
        
        # 5. Associar usuários admin ao grupo Admin
        print("👥 Associando usuários admin ao grupo...")
        cursor.execute("SELECT id, name FROM users WHERE role = 'admin'")
        admin_users = cursor.fetchall()
        
        for user_id, user_name in admin_users:
            print(f"  ✅ Associando {user_name} ao grupo Admin...")
            cursor.execute('UPDATE users SET group_id = ? WHERE id = ?', (admin_group_id, user_id))
        
        # 6. Commit das alterações
        conn.commit()
        
        # 7. Verificar resultado
        print("\n🔍 Verificando resultado...")
        cursor.execute('''
            SELECT COUNT(*) FROM group_permissions WHERE group_id = ?
        ''', (admin_group_id,))
        
        total_perms = cursor.fetchone()[0]
        print(f"✅ Total de permissões configuradas: {total_perms}")
        
        # 8. Verificar permissão específica
        cursor.execute('''
            SELECT permission_value FROM group_permissions 
            WHERE group_id = ? AND permission_name = 'reply_rncs'
        ''', (admin_group_id,))
        
        reply_perm = cursor.fetchone()
        if reply_perm and reply_perm[0]:
            print("✅ Permissão 'reply_rncs' configurada e ativa!")
        else:
            print("❌ Permissão 'reply_rncs' não configurada!")
        
        conn.close()
        
        print("\n🎉 Permissões do admin corrigidas com sucesso!")
        print("✅ Agora o admin pode responder RNCs sem problemas!")
        
    except Exception as e:
        print(f"❌ Erro ao corrigir permissões: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_admin_permissions()
