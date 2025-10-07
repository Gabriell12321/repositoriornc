#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def simple_test():
    """Teste simples de conexão"""
    print("🔍 Teste Simples de Banco de Dados")
    print("=" * 40)
    
    try:
        # 1. Verificar arquivo
        print("1. Verificando arquivo...")
        if os.path.exists('ippel_system.db'):
            print("   ✅ Arquivo existe")
            print(f"   📏 Tamanho: {os.path.getsize('ippel_system.db')} bytes")
        else:
            print("   ❌ Arquivo não existe")
            return
        
        # 2. Tentar conectar
        print("\n2. Conectando...")
        conn = sqlite3.connect('ippel_system.db', timeout=30.0)
        print("   ✅ Conexão criada")
        
        # 3. Criar cursor
        print("\n3. Criando cursor...")
        cursor = conn.cursor()
        print("   ✅ Cursor criado")
        
        # 4. Testar PRAGMA simples
        print("\n4. Testando PRAGMA...")
        cursor.execute('PRAGMA user_version')
        version = cursor.fetchone()[0]
        print(f"   ✅ User version: {version}")
        
        # 5. Listar tabelas
        print("\n5. Listando tabelas...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"   📋 Tabelas encontradas: {len(tables)}")
        for table in tables:
            print(f"      - {table[0]}")
        
        # 6. Testar consulta em users
        if tables and any('users' in table[0] for table in tables):
            print("\n6. Testando consulta em users...")
            cursor.execute('SELECT COUNT(*) FROM users')
            count = cursor.fetchone()[0]
            print(f"   👥 Usuários: {count}")
        
        # 7. Testar consulta em rncs
        if tables and any('rncs' in table[0] for table in tables):
            print("\n7. Testando consulta em rncs...")
            cursor.execute('SELECT COUNT(*) FROM rncs')
            count = cursor.fetchone()[0]
            print(f"   📋 RNCs: {count}")
        
        conn.close()
        print("\n✅ Todos os testes passaram!")
        return True
        
    except sqlite3.OperationalError as e:
        print(f"\n❌ Erro operacional: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return False

def recreate_simple_db():
    """Recriar banco de dados de forma mais simples"""
    print("\n🔧 Recriando banco de dados...")
    
    try:
        # Remover arquivos
        for file in ['ippel_system.db', 'ippel_system.db-shm', 'ippel_system.db-wal']:
            if os.path.exists(file):
                os.remove(file)
                print(f"   🗑️ Removido: {file}")
        
        # Criar novo banco
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Criar tabela users
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT UNIQUE,
                password_hash TEXT,
                department TEXT,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Criar tabela rncs
        cursor.execute('''
            CREATE TABLE rncs (
                id INTEGER PRIMARY KEY,
                rnc_number TEXT UNIQUE,
                title TEXT,
                description TEXT,
                user_id INTEGER,
                status TEXT DEFAULT 'Pendente',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Inserir usuário admin
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, department, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Admin', 'admin@ippel.com.br', 'hash123', 'TI', 'admin'))
        
        conn.commit()
        conn.close()
        
        print("   ✅ Banco recriado com sucesso!")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

if __name__ == '__main__':
    if not simple_test():
        print("\n🔄 Tentando recriar banco...")
        if recreate_simple_db():
            print("\n🧪 Testando novamente...")
            simple_test()
        else:
            print("\n❌ Falha ao recriar banco.") 