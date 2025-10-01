#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_user_data():
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        print("=== VERIFICANDO USUÁRIO ID 2 ===")
        cursor.execute('SELECT * FROM users WHERE id = 2')
        user = cursor.fetchone()
        print(f"Dados completos do usuário ID 2: {user}")
        
        # Verificar colunas
        cursor.execute('PRAGMA table_info(users)')
        columns = cursor.fetchall()
        print("\nEstrutura da tabela users:")
        for i, col in enumerate(columns):
            print(f"  Coluna {i}: {col[1]} ({col[2]})")
        
        # Verificar se esse nome existe em algum lugar
        print("\n=== PROCURANDO 'Elvio Silva' ===")
        cursor.execute("SELECT * FROM users WHERE name LIKE '%Elvio%' OR name LIKE '%Silva%'")
        elvio_users = cursor.fetchall()
        for user in elvio_users:
            print(f"Usuário encontrado: {user}")
        
        # Verificar todos os usuários
        print("\n=== TODOS OS USUÁRIOS ===")
        cursor.execute('SELECT id, name, email, department FROM users ORDER BY id')
        all_users = cursor.fetchall()
        for user in all_users:
            print(f"ID {user[0]}: {user[1]} - {user[2]} ({user[3]})")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    check_user_data()
