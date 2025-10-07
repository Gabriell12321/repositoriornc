#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script direto para corrigir permissões do sistema
"""

import sqlite3

def fix_permissions_direct():
    """Corrige as permissões diretamente no banco"""
    
    try:
        print("🔧 Corrigindo permissões do sistema...")
        
        # Conectar ao banco
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # 1. Adicionar permissão reply_rncs para todos os grupos
        print("✅ Adicionando permissão 'reply_rncs'...")
        cursor.execute('''
            INSERT OR IGNORE INTO group_permissions (group_id, permission_name, permission_value)
            SELECT g.id, 'reply_rncs', 1
            FROM groups g
            WHERE NOT EXISTS (
                SELECT 1 FROM group_permissions gp 
                WHERE gp.group_id = g.id AND gp.permission_name = 'reply_rncs'
            )
        ''')
        
        # 2. Adicionar outras permissões importantes
        important_permissions = ['share_rncs', 'finalize_rncs', 'assign_rncs']
        
        for permission in important_permissions:
            print(f"✅ Adicionando permissão '{permission}'...")
            cursor.execute('''
                INSERT OR IGNORE INTO group_permissions (group_id, permission_name, permission_value)
                SELECT g.id, ?, 1
                FROM groups g
                WHERE NOT EXISTS (
                    SELECT 1 FROM group_permissions gp 
                    WHERE gp.group_id = g.id AND gp.permission_name = ?
                )
            ''', (permission, permission))
        
        # 3. Commit das alterações
        conn.commit()
        
        # 4. Verificar resultado
        print("\n🔍 Verificando permissões após correção...")
        
        cursor.execute('''
            SELECT g.name as grupo, COUNT(gp.permission_name) as total_permissoes
            FROM groups g
            LEFT JOIN group_permissions gp ON g.id = gp.group_id
            GROUP BY g.id, g.name
            ORDER BY g.name
        ''')
        
        results = cursor.fetchall()
        for grupo, total in results:
            print(f"  👥 {grupo}: {total} permissões")
        
        # 5. Verificar permissão específica
        print(f"\n🎯 Verificando permissão 'reply_rncs':")
        cursor.execute('''
            SELECT g.name, gp.permission_value 
            FROM groups g 
            LEFT JOIN group_permissions gp ON g.id = gp.group_id AND gp.permission_name = 'reply_rncs'
        ''')
        
        reply_perms = cursor.fetchall()
        for group_name, perm_value in reply_perms:
            status = "✅ CONFIGURADA" if perm_value else "❌ NÃO CONFIGURADA"
            print(f"  - {group_name}: {status}")
        
        conn.close()
        
        print("\n🎉 Permissões corrigidas com sucesso!")
        print("✅ Agora todos os usuários podem responder RNCs!")
        
    except Exception as e:
        print(f"❌ Erro ao corrigir permissões: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_permissions_direct()
