#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar estrutura do banco de dados para grupos e permissões
"""
import sqlite3

def check_db_structure():
    """Verificar estrutura do banco"""
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Listar todas as tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print("📋 Tabelas no banco:")
    for table in sorted(tables):
        print(f"   - {table}")
    
    # Verificar se existe tabela groups
    if 'groups' in tables:
        print("\n🏢 Estrutura da tabela 'groups':")
        cursor.execute("PRAGMA table_info(groups)")
        for row in cursor.fetchall():
            print(f"   {row}")
        
        print("\n📊 Grupos existentes:")
        cursor.execute("SELECT id, name, description FROM groups")
        for row in cursor.fetchall():
            print(f"   {row[0]}: {row[1]} - {row[2]}")
    else:
        print("\n⚠️ Tabela 'groups' não existe")
    
    # Verificar se existe tabela group_permissions
    if 'group_permissions' in tables:
        print("\n🔐 Estrutura da tabela 'group_permissions':")
        cursor.execute("PRAGMA table_info(group_permissions)")
        for row in cursor.fetchall():
            print(f"   {row}")
        
        print("\n📊 Exemplo de permissões:")
        cursor.execute("SELECT * FROM group_permissions LIMIT 10")
        for row in cursor.fetchall():
            print(f"   {row}")
    else:
        print("\n⚠️ Tabela 'group_permissions' não existe")
    
    # Verificar usuários e seus grupos
    print("\n👤 Usuários e grupos:")
    cursor.execute("SELECT id, name, email, group_id, department FROM users LIMIT 10")
    for row in cursor.fetchall():
        print(f"   {row}")
    
    conn.close()

if __name__ == "__main__":
    check_db_structure()
