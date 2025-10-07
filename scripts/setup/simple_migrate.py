#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simples para verificar e migrar banco de dados
"""

import sqlite3
import os

def main():
    db_path = "database.db"
    
    print(f"🔍 Verificando banco de dados: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ Arquivo database.db não encontrado!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tabela users
        cursor.execute("PRAGMA table_info(users)")
        users_columns = cursor.fetchall()
        print(f"📊 Colunas da tabela users: {len(users_columns)}")
        
        for col in users_columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Verificar se group_id existe
        has_group_id = any(col[1] == 'group_id' for col in users_columns)
        has_active = any(col[1] == 'active' for col in users_columns)
        
        print(f"🔍 Coluna group_id existe: {has_group_id}")
        print(f"🔍 Coluna active existe: {has_active}")
        
        # Verificar tabela groups
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='groups'")
        groups_table = cursor.fetchone()
        print(f"🔍 Tabela groups existe: {groups_table is not None}")
        
        if not has_group_id:
            print("➕ Adicionando coluna group_id...")
            cursor.execute("ALTER TABLE users ADD COLUMN group_id INTEGER DEFAULT 1")
            
        if not has_active:
            print("➕ Adicionando coluna active...")
            cursor.execute("ALTER TABLE users ADD COLUMN active BOOLEAN DEFAULT 1")
        
        if not groups_table:
            print("➕ Criando tabela groups...")
            cursor.execute('''
                CREATE TABLE groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT
                )
            ''')
            
            # Inserir grupos padrão
            groups = [
                (1, 'Administradores', 'Grupo com acesso total'),
                (2, 'Engenharia', 'Equipe de engenharia'),
                (3, 'Qualidade', 'Equipe de qualidade'),
                (4, 'Operadores', 'Operadores do sistema'),
                (5, 'Gerentes', 'Gerentes e supervisores')
            ]
            
            cursor.executemany('INSERT OR IGNORE INTO groups (id, name, description) VALUES (?, ?, ?)', groups)
        
        conn.commit()
        conn.close()
        
        print("✅ Migração concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()