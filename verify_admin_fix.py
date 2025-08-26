#!/usr/bin/env python3
import sqlite3

def verify_fix():
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    print("🔍 Verificando correção das permissões...")
    
    # 1. Verificar grupo Admin
    cursor.execute("SELECT id, name FROM groups WHERE name = 'Administrador'")
    admin_group = cursor.fetchone()
    
    if admin_group:
        group_id, group_name = admin_group
        print(f"✅ Grupo {group_name} encontrado (ID: {group_id})")
        
        # 2. Verificar permissão reply_rncs
        cursor.execute("SELECT permission_value FROM group_permissions WHERE group_id = ? AND permission_name = 'reply_rncs'", (group_id,))
        reply_perm = cursor.fetchone()
        
        if reply_perm and reply_perm[0]:
            print("✅ Permissão 'reply_rncs' configurada e ativa!")
        else:
            print("❌ Permissão 'reply_rncs' não configurada!")
        
        # 3. Verificar usuários admin associados
        cursor.execute("SELECT id, name, role FROM users WHERE group_id = ? AND role = 'admin'", (group_id,))
        admin_users = cursor.fetchall()
        
        if admin_users:
            print(f"✅ {len(admin_users)} usuários admin associados ao grupo:")
            for user_id, name, role in admin_users:
                print(f"  - {name} (ID: {user_id}, Role: {role})")
        else:
            print("❌ Nenhum usuário admin associado ao grupo!")
        
        # 4. Verificar total de permissões
        cursor.execute("SELECT COUNT(*) FROM group_permissions WHERE group_id = ?", (group_id,))
        total_perms = cursor.fetchone()[0]
        print(f"📊 Total de permissões configuradas: {total_perms}")
        
    else:
        print("❌ Grupo Admin não encontrado!")
    
    conn.close()

if __name__ == "__main__":
    verify_fix()
