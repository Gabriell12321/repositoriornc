#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para atualizar e configurar permissões do sistema
"""

import sqlite3
import json

def update_system_permissions():
    """Atualiza as permissões do sistema"""
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        print("🔧 Atualizando permissões do sistema...")
        
        # Verificar se a tabela group_permissions existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='group_permissions'")
        if not cursor.fetchone():
            print("❌ Tabela 'group_permissions' não encontrada!")
            return
        
        # Lista de todas as permissões disponíveis
        all_permissions = [
            'create_rnc',
            'update_avatar', 
            'edit_own_rnc',
            'view_own_rnc',
            'view_all_rncs',
            'edit_all_rncs',
            'delete_rnc',
            'reply_rncs',  # PERMISSÃO QUE ESTAVA FALTANDO!
            'share_rncs',
            'finalize_rncs',
            'assign_rncs',
            'view_finalized_rncs',
            'view_charts',
            'view_reports',
            'export_data',
            'admin_access',
            'manage_users',
            'manage_groups',
            'view_engineering_rncs',
            'view_all_departments_rncs',
            'view_levantamento_14_15',
            'view_groups_for_assignment',
            'view_users_for_assignment',
            'view_audit_logs',
            'manage_system_settings'
        ]
        
        print(f"✅ Total de permissões: {len(all_permissions)}")
        
        # Verificar grupos existentes
        cursor.execute("SELECT id, name FROM groups")
        groups = cursor.fetchall()
        
        if not groups:
            print("❌ Nenhum grupo encontrado!")
            return
        
        print(f"✅ Grupos encontrados: {len(groups)}")
        
        # Para cada grupo, configurar permissões padrão
        for group_id, group_name in groups:
            print(f"\n🔧 Configurando grupo: {group_name}")
            
            # Limpar permissões existentes
            cursor.execute('DELETE FROM group_permissions WHERE group_id = ?', (group_id,))
            
            # Configurar permissões baseadas no tipo de grupo
            if group_name.lower() in ['admin', 'administrador', 'administração']:
                # Admin tem todas as permissões
                permissions_to_grant = all_permissions
                print("  👑 Admin: Todas as permissões")
                
            elif group_name.lower() in ['gerente', 'supervisor', 'coordenador']:
                # Gerentes têm permissões avançadas
                permissions_to_grant = [
                    'create_rnc', 'edit_own_rnc', 'view_own_rnc', 'view_all_rncs',
                    'edit_all_rncs', 'reply_rncs', 'share_rncs', 'finalize_rncs',
                    'assign_rncs', 'view_finalized_rncs', 'view_charts', 'view_reports',
                    'view_engineering_rncs', 'view_all_departments_rncs',
                    'view_groups_for_assignment', 'view_users_for_assignment'
                ]
                print("  👔 Gerente: Permissões avançadas")
                
            elif group_name.lower() in ['engenharia', 'engenheiro']:
                # Engenharia tem permissões específicas
                permissions_to_grant = [
                    'create_rnc', 'edit_own_rnc', 'view_own_rnc', 'view_all_rncs',
                    'reply_rncs', 'share_rncs', 'view_finalized_rncs',
                    'view_engineering_rncs', 'view_charts', 'view_reports'
                ]
                print("  🔧 Engenharia: Permissões específicas")
                
            elif group_name.lower() in ['qualidade', 'inspetor']:
                # Qualidade tem permissões de inspeção
                permissions_to_grant = [
                    'create_rnc', 'edit_own_rnc', 'view_own_rnc', 'view_all_rncs',
                    'reply_rncs', 'share_rncs', 'finalize_rncs',
                    'view_finalized_rncs', 'view_charts', 'view_reports'
                ]
                print("  ✅ Qualidade: Permissões de inspeção")
                
            else:
                # Usuários padrão têm permissões básicas
                permissions_to_grant = [
                    'create_rnc', 'edit_own_rnc', 'view_own_rnc',
                    'reply_rncs', 'view_finalized_rncs'
                ]
                print("  👤 Usuário padrão: Permissões básicas")
            
            # Inserir permissões no banco
            for permission in permissions_to_grant:
                cursor.execute('''
                    INSERT INTO group_permissions (group_id, permission_name, permission_value)
                    VALUES (?, ?, 1)
                ''', (group_id, permission))
            
            print(f"  ✅ {len(permissions_to_grant)} permissões configuradas")
        
        # Commit das alterações
        conn.commit()
        conn.close()
        
        print("\n🎉 Permissões atualizadas com sucesso!")
        print("✅ Sistema agora tem todas as permissões necessárias configuradas")
        
    except Exception as e:
        print(f"❌ Erro ao atualizar permissões: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_system_permissions()
