#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import sys

def test_database_connection():
    """Testar conexão com o banco de dados"""
    print("🧪 Testando conexão com banco de dados...")
    print("=" * 50)
    
    # Verificar se o arquivo existe
    db_path = 'ippel_system.db'
    print(f"📁 Verificando arquivo: {db_path}")
    print(f"   Existe: {os.path.exists(db_path)}")
    
    if os.path.exists(db_path):
        print(f"   Tamanho: {os.path.getsize(db_path)} bytes")
        print(f"   Permissões: {oct(os.stat(db_path).st_mode)[-3:]}")
    
    # Tentar conectar
    print("\n🔌 Tentando conectar...")
    try:
        conn = sqlite3.connect(db_path, timeout=30.0)
        print("✅ Conexão estabelecida com sucesso!")
        
        cursor = conn.cursor()
        
        # Testar consulta simples
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        print(f"   Usuários no banco: {user_count}")
        
        cursor.execute('SELECT COUNT(*) FROM rncs')
        rnc_count = cursor.fetchone()[0]
        print(f"   RNCs no banco: {rnc_count}")
        
        # Testar PRAGMA commands
        print("\n🔧 Testando comandos PRAGMA...")
        
        try:
            cursor.execute('PRAGMA journal_mode=WAL')
            journal_mode = cursor.fetchone()[0]
            print(f"   Journal mode: {journal_mode}")
        except Exception as e:
            print(f"   ❌ Erro no journal_mode: {e}")
        
        try:
            cursor.execute('PRAGMA synchronous=NORMAL')
            print("   ✅ synchronous=NORMAL aplicado")
        except Exception as e:
            print(f"   ❌ Erro no synchronous: {e}")
        
        try:
            cursor.execute('PRAGMA cache_size=10000')
            print("   ✅ cache_size aplicado")
        except Exception as e:
            print(f"   ❌ Erro no cache_size: {e}")
        
        try:
            cursor.execute('PRAGMA temp_store=MEMORY')
            print("   ✅ temp_store aplicado")
        except Exception as e:
            print(f"   ❌ Erro no temp_store: {e}")
        
        try:
            cursor.execute('PRAGMA mmap_size=268435456')
            print("   ✅ mmap_size aplicado")
        except Exception as e:
            print(f"   ❌ Erro no mmap_size: {e}")
        
        conn.close()
        print("\n✅ Todos os testes passaram!")
        return True
        
    except sqlite3.OperationalError as e:
        print(f"❌ Erro operacional: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def check_file_permissions():
    """Verificar permissões do arquivo"""
    print("\n🔐 Verificando permissões...")
    
    try:
        # Tentar abrir o arquivo para escrita
        with open('ippel_system.db', 'r+b') as f:
            print("✅ Arquivo pode ser aberto para leitura/escrita")
    except PermissionError:
        print("❌ Erro de permissão ao abrir arquivo")
        return False
    except Exception as e:
        print(f"❌ Erro ao abrir arquivo: {e}")
        return False
    
    return True

def try_recreate_database():
    """Tentar recriar o banco de dados"""
    print("\n🔧 Tentando recriar banco de dados...")
    
    try:
        # Remover arquivos existentes
        files_to_remove = ['ippel_system.db', 'ippel_system.db-shm', 'ippel_system.db-wal']
        for file in files_to_remove:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    print(f"🗑️ Removido: {file}")
                except Exception as e:
                    print(f"⚠️ Erro ao remover {file}: {e}")
        
        # Criar novo banco
        conn = sqlite3.connect('ippel_system.db', timeout=30.0)
        cursor = conn.cursor()
        
        # Criar tabela simples
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        ''')
        
        # Inserir dados de teste
        cursor.execute('INSERT INTO test_table (name) VALUES (?)', ('test',))
        
        conn.commit()
        conn.close()
        
        print("✅ Banco de dados recriado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao recriar banco: {e}")
        return False

def main():
    print("🔍 Diagnóstico do Banco de Dados")
    print("=" * 50)
    
    # Teste 1: Verificar permissões
    if not check_file_permissions():
        print("\n❌ Problema de permissões detectado!")
        return
    
    # Teste 2: Testar conexão
    if not test_database_connection():
        print("\n❌ Problema de conexão detectado!")
        
        # Tentar recriar banco
        print("\n🔄 Tentando recriar banco de dados...")
        if try_recreate_database():
            print("\n🧪 Testando nova conexão...")
            if test_database_connection():
                print("\n✅ Problema resolvido!")
            else:
                print("\n❌ Problema persiste após recriação.")
        else:
            print("\n❌ Não foi possível recriar o banco de dados.")
        return
    
    print("\n✅ Banco de dados está funcionando corretamente!")

if __name__ == '__main__':
    main() 