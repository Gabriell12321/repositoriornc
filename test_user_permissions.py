#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar permissões de um usuário específico
"""

import sqlite3
import sys

DB_PATH = 'ippel_system.db'

def test_user_permissions(user_id):
    """Testa todas as permissões de um usuário"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("=" * 60)
        print(f"🔍 TESTANDO PERMISSÕES DO USUÁRIO ID: {user_id}")
        print("=" * 60)
        
        # Buscar dados do usuário
        cursor.execute("""
            SELECT id, name, email, department, role, group_id, permissions
            FROM users WHERE id = ?
        """, (user_id,))
        
        user_data = cursor.fetchone()
        
        if not user_data:
            print(f"❌ Usuário ID {user_id} não encontrado!")
            conn.close()
            return
        
        user_id, name, email, department, role, group_id, permissions_json = user_data
        
        print(f"\n👤 Dados do Usuário:")
        print(f"   Nome: {name}")
        print(f"   Email: {email}")
        print(f"   Departamento: {department}")
        print(f"   Role: {role}")
        print(f"   Group ID: {group_id}")
        
        # Permissões diretas do usuário
        print(f"\n🔑 Permissões Diretas (JSON):")
        if permissions_json:
            import json
            try:
                perms = json.loads(permissions_json)
                if perms:
                    for perm in perms:
                        print(f"   ✅ {perm}")
                else:
                    print("   (Nenhuma permissão direta)")
            except:
                print(f"   ⚠️ Erro ao parsear JSON: {permissions_json}")
        else:
            print("   (Nenhuma permissão direta)")
        
        # Permissões do grupo
        if group_id:
            print(f"\n👥 Grupo:")
            cursor.execute("SELECT name, description FROM groups WHERE id = ?", (group_id,))
            group_data = cursor.fetchone()
            if group_data:
                print(f"   Nome: {group_data[0]}")
                print(f"   Descrição: {group_data[1]}")
                
                # Buscar permissões do grupo
                cursor.execute("""
                    SELECT permission_name, permission_value
                    FROM group_permissions
                    WHERE group_id = ?
                """, (group_id,))
                
                group_perms = cursor.fetchall()
                
                print(f"\n🔐 Permissões do Grupo ({len(group_perms)} permissões):")
                
                active_perms = [p for p in group_perms if p[1]]
                inactive_perms = [p for p in group_perms if not p[1]]
                
                if active_perms:
                    print("\n   ✅ ATIVAS:")
                    for perm_name, perm_value in active_perms:
                        print(f"      • {perm_name}")
                
                if inactive_perms:
                    print("\n   ❌ INATIVAS:")
                    for perm_name, perm_value in inactive_perms:
                        print(f"      • {perm_name}")
                
                # Verificar permissão específica reply_rncs
                print("\n🎯 Permissão Específica: 'reply_rncs'")
                cursor.execute("""
                    SELECT permission_value
                    FROM group_permissions
                    WHERE group_id = ? AND permission_name = 'reply_rncs'
                """, (group_id,))
                
                reply_perm = cursor.fetchone()
                if reply_perm:
                    if reply_perm[0]:
                        print("   ✅ ATIVA - Usuário PODE responder RNCs")
                    else:
                        print("   ❌ INATIVA - Usuário NÃO PODE responder RNCs")
                else:
                    print("   ⚠️ NÃO CONFIGURADA - Permissão não existe para este grupo")
        else:
            print("\n⚠️ Usuário não pertence a nenhum grupo!")
        
        # Admin access
        print("\n🔐 Permissão de Admin:")
        if role and role.lower() == 'admin':
            print("   ✅ Usuário é ADMIN (role='admin')")
        else:
            cursor.execute("""
                SELECT permission_value
                FROM group_permissions
                WHERE group_id = ? AND permission_name = 'admin_access'
            """, (group_id,))
            
            admin_perm = cursor.fetchone()
            if admin_perm and admin_perm[0]:
                print("   ✅ Usuário tem permissão 'admin_access' via grupo")
            else:
                print("   ❌ Usuário NÃO é admin")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ TESTE CONCLUÍDO")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        user_id = int(sys.argv[1])
    else:
        print("Uso: python test_user_permissions.py <user_id>")
        print("\nUsuários disponíveis:")
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email FROM users WHERE is_active = 1 ORDER BY id")
            users = cursor.fetchall()
            for uid, name, email in users:
                print(f"  ID: {uid} - {name} ({email})")
            conn.close()
        except:
            pass
        sys.exit(1)
    
    test_user_permissions(user_id)
