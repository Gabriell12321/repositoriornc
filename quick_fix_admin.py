#!/usr/bin/env python3
import sqlite3

def quick_fix():
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    print("🔧 Corrigindo permissões do admin...")
    
    # 1. Criar grupo Admin
    cursor.execute("INSERT OR IGNORE INTO groups (name, description) VALUES (?, ?)", 
                   ('Administrador', 'Grupo com todas as permissões'))
    
    # 2. Obter ID do grupo
    cursor.execute("SELECT id FROM groups WHERE name = 'Administrador'")
    admin_group_id = cursor.fetchone()[0]
    
    # 3. Adicionar permissão crítica
    cursor.execute("INSERT OR REPLACE INTO group_permissions (group_id, permission_name, permission_value) VALUES (?, ?, ?)", 
                   (admin_group_id, 'reply_rncs', 1))
    
    # 4. Associar usuários admin
    cursor.execute("UPDATE users SET group_id = ? WHERE role = 'admin'", (admin_group_id,))
    
    conn.commit()
    conn.close()
    
    print("✅ Permissões corrigidas!")

if __name__ == "__main__":
    quick_fix()
