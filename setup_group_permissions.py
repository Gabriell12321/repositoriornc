#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurar Permissões por Grupo
"""
import sqlite3
import json

def setup_group_permissions():
    """Configurar permissões específicas para cada grupo"""
    
    # Definir permissões por grupo
    group_permissions = {
        'Engenharia': {
            'view_own_rncs': True,
            'create_rnc': True,
            'edit_own_rnc': True,
            'view_technical_data': True,
            'technical_analysis': True,
            'view_engineering_reports': True,
            'assign_to_engineering': True,
            'view_charts': False,
            'view_all_rncs': False,
            'view_finalized_rncs': False,
            'admin_access': False,
            'manage_users': False
        },
        'Qualidade': {
            'view_own_rncs': True,
            'view_all_rncs': True,
            'view_finalized_rncs': True,
            'create_rnc': True,
            'edit_own_rnc': True,
            'edit_all_rncs': True,
            'finalize_rnc': True,
            'quality_control': True,
            'approve_rncs': True,
            'view_charts': True,
            'view_reports': True,
            'audit_rncs': True,
            'assign_to_quality': True,
            'admin_access': False,
            'manage_users': False
        },
        'TI': {
            'view_own_rncs': True,
            'view_all_rncs': True,
            'view_finalized_rncs': True,
            'view_charts': True,
            'view_reports': True,
            'create_rnc': True,
            'edit_own_rnc': True,
            'edit_all_rncs': True,
            'delete_rncs': True,
            'finalize_rnc': True,
            'admin_access': True,
            'manage_users': True,
            'system_config': True,
            'backup_system': True,
            'view_audit_logs': True,
            'assign_to_any': True
        },
        'Produção': {
            'view_own_rncs': True,
            'create_rnc': True,
            'edit_own_rnc': True,
            'view_production_data': True,
            'production_analysis': True,
            'assign_to_production': True,
            'view_charts': False,
            'view_all_rncs': False,
            'view_finalized_rncs': False,
            'admin_access': False,
            'manage_users': False
        },
        'Administração': {
            'view_own_rncs': True,
            'view_all_rncs': True,
            'view_finalized_rncs': True,
            'view_charts': True,
            'view_reports': True,
            'create_rnc': True,
            'edit_own_rnc': True,
            'edit_all_rncs': True,
            'finalize_rnc': True,
            'admin_access': True,
            'manage_users': True,
            'view_admin_reports': True,
            'assign_to_any': True,
            'financial_analysis': True
        }
    }
    
    print("🔧 Configurando permissões por grupo...")
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    try:
        # Limpar permissões existentes
        cursor.execute("DELETE FROM group_permissions")
        print("🗑️ Permissões antigas removidas")
        
        # Obter mapeamento de grupos
        cursor.execute("SELECT id, name FROM groups")
        groups = {name: group_id for group_id, name in cursor.fetchall()}
        
        # Inserir novas permissões
        total_permissions = 0
        for group_name, permissions in group_permissions.items():
            if group_name in groups:
                group_id = groups[group_name]
                print(f"\n🏢 Configurando grupo: {group_name} (ID: {group_id})")
                
                for permission_name, permission_value in permissions.items():
                    cursor.execute('''
                        INSERT INTO group_permissions (group_id, permission_name, permission_value)
                        VALUES (?, ?, ?)
                    ''', (group_id, permission_name, 1 if permission_value else 0))
                    
                    status = "✅" if permission_value else "❌"
                    print(f"   {status} {permission_name}")
                    total_permissions += 1
            else:
                print(f"⚠️ Grupo '{group_name}' não encontrado no banco")
        
        conn.commit()
        print(f"\n✅ {total_permissions} permissões configuradas com sucesso!")
        
        # Verificar resultado
        print("\n📊 Resumo das permissões por grupo:")
        for group_name, group_id in groups.items():
            cursor.execute('''
                SELECT COUNT(*) as total,
                       SUM(permission_value) as enabled
                FROM group_permissions 
                WHERE group_id = ?
            ''', (group_id,))
            result = cursor.fetchone()
            total = result[0] if result else 0
            enabled = result[1] if result else 0
            print(f"   🏢 {group_name}: {enabled}/{total} permissões ativas")
    
    except Exception as e:
        print(f"❌ Erro ao configurar permissões: {e}")
        conn.rollback()
    
    finally:
        conn.close()

def test_group_permissions():
    """Testar as permissões configuradas"""
    print("\n🧪 Testando permissões configuradas...")
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    try:
        # Obter usuários com seus grupos
        cursor.execute('''
            SELECT u.id, u.name, u.email, g.name as group_name
            FROM users u
            LEFT JOIN groups g ON u.group_id = g.id
            WHERE u.is_active = 1
            LIMIT 5
        ''')
        
        users = cursor.fetchall()
        
        for user_id, user_name, email, group_name in users:
            print(f"\n👤 {user_name} ({group_name})")
            
            if group_name:
                # Buscar permissões do grupo
                cursor.execute('''
                    SELECT gp.permission_name, gp.permission_value
                    FROM group_permissions gp
                    JOIN groups g ON g.id = gp.group_id
                    WHERE g.name = ? AND gp.permission_value = 1
                    ORDER BY gp.permission_name
                ''', (group_name,))
                
                permissions = cursor.fetchall()
                print(f"   🔑 {len(permissions)} permissões ativas:")
                for perm_name, _ in permissions[:5]:  # Mostrar apenas as primeiras 5
                    print(f"      ✅ {perm_name}")
                if len(permissions) > 5:
                    print(f"      ... e mais {len(permissions) - 5}")
            else:
                print("   ⚠️ Usuário sem grupo definido")
    
    except Exception as e:
        print(f"❌ Erro ao testar permissões: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    setup_group_permissions()
    test_group_permissions()
