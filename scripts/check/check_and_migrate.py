#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar e migrar banco de dados
"""

import sqlite3
import os

# Configuração
DB_PATH = 'database.db'

def check_and_migrate():
    """Verificar estrutura do banco e fazer migrações necessárias"""
    
    print("🔍 Verificando estrutura do banco de dados...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se tabela users existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ Tabela 'users' não encontrada!")
            conn.close()
            return False
        
        # Verificar colunas da tabela users
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Colunas na tabela users: {columns}")
        
        migrations_needed = []
        
        if 'group_id' not in columns:
            migrations_needed.append('group_id')
        
        if 'active' not in columns:
            migrations_needed.append('active')
        
        if migrations_needed:
            print(f"🔧 Migrações necessárias: {migrations_needed}")
            
            for column in migrations_needed:
                if column == 'group_id':
                    print("  ➕ Adicionando coluna group_id...")
                    cursor.execute('ALTER TABLE users ADD COLUMN group_id INTEGER')
                elif column == 'active':
                    print("  ➕ Adicionando coluna active...")
                    cursor.execute('ALTER TABLE users ADD COLUMN active BOOLEAN DEFAULT 1')
        
        # Verificar se tabela groups existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='groups'")
        if not cursor.fetchone():
            print("  ➕ Criando tabela groups...")
            cursor.execute('''
                CREATE TABLE groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Inserir grupos padrão
            print("  📝 Inserindo grupos padrão...")
            default_groups = [
                ('Administradores', 'Acesso completo ao sistema'),
                ('Engenharia', 'Equipe de engenharia'),
                ('Qualidade', 'Equipe de controle de qualidade'),
                ('Operadores', 'Operadores de produção'),
                ('Gerentes', 'Gerentes de área com permissões elevadas')
            ]
            
            for name, desc in default_groups:
                cursor.execute("INSERT INTO groups (name, description) VALUES (?, ?)", (name, desc))
        
        # Verificar quantos usuários e grupos existem
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM groups")
        group_count = cursor.fetchone()[0]
        
        print(f"👥 Usuários cadastrados: {user_count}")
        print(f"🏷️ Grupos cadastrados: {group_count}")
        
        # Listar alguns usuários
        if user_count > 0:
            cursor.execute("SELECT id, name, email, group_id, active FROM users LIMIT 5")
            users = cursor.fetchall()
            print("📋 Usuários (primeiros 5):")
            for user in users:
                print(f"  - ID: {user[0]}, Nome: {user[1]}, Email: {user[2]}, Grupo: {user[3]}, Ativo: {user[4]}")
        
        # Listar grupos
        if group_count > 0:
            cursor.execute("SELECT id, name, description FROM groups")
            groups = cursor.fetchall()
            print("🏷️ Grupos:")
            for group in groups:
                print(f"  - ID: {group[0]}, Nome: {group[1]}, Descrição: {group[2]}")
        
        conn.commit()
        conn.close()
        
        print("✅ Verificação e migração concluídas com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante migração: {e}")
        return False

if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        check_and_migrate()
    else:
        print(f"❌ Banco de dados não encontrado: {DB_PATH}")
        print("Execute o sistema principal primeiro para criar o banco.")