#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def delete_example_users():
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # IDs dos usuários para deletar
        users_to_delete = [2, 3, 4, 5, 6]  # Elvio Silva, Maria Santos, João Costa, Ana Oliveira, Evilyn
        
        print("=== VERIFICANDO USUÁRIOS ANTES DA DELEÇÃO ===")
        for user_id in users_to_delete:
            cursor.execute('SELECT id, name, email, department FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            if user:
                print(f"ID {user[0]}: {user[1]} - {user[2]} ({user[3]})")
        
        # Verificar quantas RNCs estão atribuídas a esses usuários
        print("\n=== VERIFICANDO RNCs ATRIBUÍDAS ===")
        for user_id in users_to_delete:
            cursor.execute('SELECT COUNT(*) FROM rncs WHERE user_id = ?', (user_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"Usuário ID {user_id}: {count} RNCs atribuídas")
        
        # Reatribuir as RNCs desses usuários para o administrador temporariamente
        print("\n=== REATRIBUINDO RNCs ===")
        for user_id in users_to_delete:
            cursor.execute('UPDATE rncs SET user_id = 1 WHERE user_id = ?', (user_id,))
            cursor.execute('SELECT changes()')
            changes = cursor.fetchone()[0]
            if changes > 0:
                print(f"Reatribuídas {changes} RNCs do usuário ID {user_id} para o Administrador")
        
        # Deletar os usuários
        print("\n=== DELETANDO USUÁRIOS ===")
        for user_id in users_to_delete:
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            cursor.execute('SELECT changes()')
            changes = cursor.fetchone()[0]
            if changes > 0:
                print(f"Usuário ID {user_id} deletado com sucesso")
        
        # Confirmar mudanças
        conn.commit()
        
        # Verificar usuários restantes
        print("\n=== USUÁRIOS RESTANTES ===")
        cursor.execute('SELECT id, name, email, department FROM users ORDER BY id')
        remaining_users = cursor.fetchall()
        for user in remaining_users:
            print(f"ID {user[0]}: {user[1]} - {user[2]} ({user[3]})")
        
        # Verificar distribuição atual das RNCs
        print("\n=== DISTRIBUIÇÃO ATUAL DAS RNCs ===")
        cursor.execute('''
            SELECT r.user_id, u.name, u.department, COUNT(*) as total 
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id 
            GROUP BY r.user_id, u.name, u.department 
            ORDER BY total DESC
        ''')
        rnc_counts = cursor.fetchall()
        for user_id, name, department, count in rnc_counts:
            user_info = f"{name} ({department})" if name else f"ID {user_id}"
            print(f"User ID {user_id} - {user_info}: {count} RNCs")
        
        conn.close()
        print("\n✅ Usuários de exemplo deletados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante a deleção: {e}")

if __name__ == "__main__":
    delete_example_users()
