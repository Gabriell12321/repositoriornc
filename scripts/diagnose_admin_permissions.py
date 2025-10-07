#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar permissões do usuário admin
"""

import sqlite3

def diagnose_admin_permissions():
    """Diagnostica as permissões do usuário admin"""
    
    try:
        print("🔍 Diagnosticando permissões do usuário admin...")
        
        # Conectar ao banco
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # 1. Verificar usuários admin
        print("\n👑 Verificando usuários admin...")
        cursor.execute("SELECT id, name, email, role, department FROM users WHERE role = 'admin'")
        admin_users = cursor.fetchall()
        
        if not admin_users:
            print("❌ Nenhum usuário admin encontrado!")
            return
        
        for user_id, name, email, role, dept in admin_users:
            print(f"  ✅ Admin: {name} (ID: {user_id}, Email: {email}, Dept: {dept})")
        
        # 2. Verificar estrutura da tabela users
        print("\n📋 Verificando estrutura da tabela users...")
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [row[1] for row in cursor.fetchall()]
        print(f"  Colunas: {user_columns}")
        
        # 3. Verificar estrutura da tabela groups
        print("\n👥 Verificando estrutura da tabela groups...")
        cursor.execute("PRAGMA table_info(groups)")
        group_columns = [row[1] for row in cursor.fetchall()]
        print(f"  Colunas: {group_columns}")
        
        # 4. Verificar estrutura da tabela group_permissions
        print("\n🔐 Verificando estrutura da tabela group_permissions...")
        cursor.execute("PRAGMA table_info(group_permissions)")
        perm_columns = [row[1] for row in cursor.fetchall()]
        print(f"  Colunas: {perm_columns}")
        
        # 5. Verificar grupos existentes
        print("\n🏷️ Verificando grupos existentes...")
        cursor.execute("SELECT id, name FROM groups")
        groups = cursor.fetchall()
        
        if not groups:
            print("❌ Nenhum grupo encontrado!")
            return
        
        for group_id, group_name in groups:
            print(f"  - {group_name} (ID: {group_id})")
        
        # 6. Verificar permissões de cada grupo
        print("\n🔑 Verificando permissões de cada grupo...")
        for group_id, group_name in groups:
            print(f"\n  📂 Grupo: {group_name}")
            cursor.execute('''
                SELECT permission_name, permission_value 
                FROM group_permissions 
                WHERE group_id = ?
            ''', (group_id,))
            
            permissions = cursor.fetchall()
            if not permissions:
                print("    ❌ Nenhuma permissão configurada")
            else:
                print(f"    ✅ {len(permissions)} permissões:")
                for perm_name, perm_value in permissions:
                    status = "✅ ATIVA" if perm_value else "❌ INATIVA"
                    print(f"      - {perm_name}: {status}")
        
        # 7. Verificar usuário admin específico
        if admin_users:
            admin_user = admin_users[0]
            admin_id = admin_user[0]
            admin_name = admin_user[1]
            
            print(f"\n🎯 Verificando usuário admin específico: {admin_name}")
            
            # Verificar se tem grupo
            cursor.execute("SELECT group_id FROM users WHERE id = ?", (admin_id,))
            group_result = cursor.fetchone()
            if group_result and group_result[0]:
                group_id = group_result[0]
                print(f"  📂 Grupo ID: {group_id}")
                
                # Verificar permissões do grupo
                cursor.execute('''
                    SELECT permission_name, permission_value 
                    FROM group_permissions 
                    WHERE group_id = ?
                ''', (group_id,))
                
                group_perms = cursor.fetchall()
                print(f"  🔑 Permissões do grupo: {len(group_perms)}")
                
                # Verificar permissão específica reply_rncs
                reply_perm = [p for p in group_perms if p[0] == 'reply_rncs']
                if reply_perm:
                    status = "✅ ATIVA" if reply_perm[0][1] else "❌ INATIVA"
                    print(f"    - reply_rncs: {status}")
                else:
                    print("    ❌ reply_rncs: NÃO ENCONTRADA")
            else:
                print("  ❌ Usuário não tem grupo associado")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro durante diagnóstico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_admin_permissions()
