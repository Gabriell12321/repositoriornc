#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar usuários de teste
"""
import sqlite3

def check_test_users():
    """Verificar usuários de teste"""
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Verificar usuários específicos
    cursor.execute('''
        SELECT id, name, email, group_id, department, password_hash 
        FROM users 
        WHERE email IN ('ronaldo@ippel.com.br', 'engenharia@1', 'admin@ippel.com.br')
    ''')
    
    users = cursor.fetchall()
    print("👥 Usuários de teste:")
    for user in users:
        print(f"   ID: {user[0]}")
        print(f"   Nome: {user[1]}")
        print(f"   Email: {user[2]}")
        print(f"   Group ID: {user[3]}")
        print(f"   Departamento: {user[4]}")
        print(f"   Tem senha: {'✅' if user[5] else '❌'}")
        print()
    
    # Verificar grupos
    cursor.execute('SELECT id, name FROM groups')
    groups = cursor.fetchall()
    print("🏢 Grupos disponíveis:")
    for group in groups:
        print(f"   {group[0]}: {group[1]}")
    
    conn.close()

if __name__ == "__main__":
    check_test_users()
