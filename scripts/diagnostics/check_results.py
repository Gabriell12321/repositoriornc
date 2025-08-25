#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_results():
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Contar usuários
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        print(f"Total de usuários: {total_users}")
        
        # Top 10 usuários com mais RNCs
        cursor.execute('''
            SELECT r.user_id, u.name, u.department, COUNT(*) as total 
            FROM rncs r 
            LEFT JOIN users u ON r.user_id = u.id 
            GROUP BY r.user_id, u.name, u.department 
            ORDER BY total DESC 
            LIMIT 10
        ''')
        print("\nTop 10 usuários com mais RNCs:")
        for row in cursor.fetchall():
            user_info = f"{row[1]} ({row[2]})" if row[1] else f"ID {row[0]}"
            print(f"ID {row[0]}: {user_info} - {row[3]} RNCs")
        
        # Verificar se ainda há RNCs com administrador
        cursor.execute('SELECT COUNT(*) FROM rncs WHERE user_id = 1')
        admin_rncs = cursor.fetchone()[0]
        print(f"\nRNCs ainda atribuídas ao Administrador: {admin_rncs}")
        
        # Total de RNCs
        cursor.execute('SELECT COUNT(*) FROM rncs')
        total_rncs = cursor.fetchone()[0]
        print(f"Total de RNCs: {total_rncs}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    check_results()
