#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys

def check_rnc_creators():
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Verificar se existe tabela de usuários
        print("=== TABELAS NO BANCO ===")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"Tabela: {table[0]}")
        
        # Verificar estrutura da tabela users
        print("\n=== ESTRUTURA DA TABELA USERS ===")
        try:
            cursor.execute('PRAGMA table_info(users)')
            columns = cursor.fetchall()
            for col in columns:
                print(f"Coluna: {col[1]} | Tipo: {col[2]}")
        except Exception as e:
            print(f"Erro ao acessar tabela users: {e}")
        
        # Verificar usuários no sistema
        print("\n=== USUÁRIOS NO SISTEMA ===")
        try:
            cursor.execute('SELECT id, name, email, department FROM users ORDER BY id')
            users = cursor.fetchall()
            for user in users:
                print(f"ID: {user[0]} | Nome: {user[1]} | Email: {user[2]} | Depto: {user[3]}")
        except Exception as e:
            print(f"Erro ao buscar usuários: {e}")
        
        # Verificar RNCs por user_id
        print("\n=== RNCs POR USUÁRIO (user_id) ===")
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
        
        print("\n=== PRIMEIRAS 10 RNCs COM USUÁRIOS ===")
        cursor.execute('''
            SELECT r.id, r.rnc_number, r.user_id, u.name, u.department, r.created_at
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id 
            ORDER BY r.id 
            LIMIT 10
        ''')
        rncs = cursor.fetchall()
        for rnc in rncs:
            user_info = f"{rnc[3]} ({rnc[4]})" if rnc[3] else f"ID {rnc[2]}"
            print(f"RNC {rnc[1]} (ID: {rnc[0]}) | Criado por: {user_info} | Data: {rnc[5]}")
        
        print(f"\n=== TOTAL DE RNCs NO SISTEMA ===")
        cursor.execute('SELECT COUNT(*) FROM rncs')
        total = cursor.fetchone()[0]
        print(f"Total de RNCs: {total}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {e}")

if __name__ == "__main__":
    check_rnc_creators()
