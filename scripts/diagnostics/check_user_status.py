#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar se usuários estão ativos
"""
import sqlite3

def check_user_status():
    """Verificar status dos usuários"""
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT name, email, is_active, password_hash 
        FROM users 
        WHERE email IN ('ronaldo@ippel.com.br', 'engenharia@1', 'admin@ippel.com.br')
    ''')
    
    users = cursor.fetchall()
    print("👥 Status dos usuários:")
    for user in users:
        print(f"   📧 {user[1]}")
        print(f"   👤 {user[0]}")
        print(f"   ✅ Ativo: {'Sim' if user[2] else 'Não'}")
        print(f"   🔐 Hash da senha: {user[3][:20]}...")
        print()
    
    # Ativar usuários se necessário
    cursor.execute('UPDATE users SET is_active = 1 WHERE email IN (?, ?)', 
                   ('ronaldo@ippel.com.br', 'engenharia@1'))
    conn.commit()
    print("✅ Usuários ativados")
    
    conn.close()

if __name__ == "__main__":
    check_user_status()
