#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar a estrutura do banco de dados
"""

import sqlite3

def check_database_structure():
    """Verifica a estrutura do banco de dados"""
    db_files = ['ippel_system.db', 'database.db', 'ippel_system_new.db']
    
    for db_file in db_files:
        print(f"\n📊 VERIFICANDO {db_file}:")
        print("=" * 50)
        
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Listar todas as tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = cursor.fetchall()
            
            if not tables:
                print("   ⚠️ Banco vazio ou sem tabelas")
                conn.close()
                continue
            
            print(f"   🗄️ TABELAS ({len(tables)}):")
            for table in tables:
                print(f"   • {table[0]}")
            
            # Verificar estrutura da tabela users
            if any('users' in table for table in tables):
                print(f"\n   👤 ESTRUTURA DA TABELA USERS:")
                cursor.execute("PRAGMA table_info(users)")
                columns = cursor.fetchall()
                for col in columns:
                    print(f"   • {col[1]} ({col[2]})")
                
                # Verificar alguns usuários
                cursor.execute("SELECT id, username, role, department FROM users LIMIT 5")
                users = cursor.fetchall()
                print(f"\n   👥 USUÁRIOS EXEMPLO ({len(users)}):")
                for user in users:
                    print(f"   • ID {user[0]}: {user[1]} ({user[2]}) - {user[3]}")
            
            # Verificar se há tabelas de grupos/permissões
            group_tables = [t[0] for t in tables if 'group' in t[0].lower() or 'permission' in t[0].lower()]
            if group_tables:
                print(f"\n   🔐 TABELAS DE PERMISSÕES:")
                for table in group_tables:
                    print(f"   • {table}")
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"     ({count} registros)")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Erro ao verificar {db_file}: {e}")

if __name__ == "__main__":
    check_database_structure()
