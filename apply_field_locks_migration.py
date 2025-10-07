#!/usr/bin/env python3
"""
Script para aplicar migração de contextos ao sistema de field locks
Adiciona suporte para permissões separadas de Criação e Resposta
"""

import sqlite3
import os
from datetime import datetime

# Caminho do banco de dados
DB_PATH = 'ippel_system.db'
MIGRATION_FILE = 'migrations/add_context_to_field_locks.sql'

def apply_migration():
    """Aplica a migração de contextos na tabela field_locks"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Erro: Banco de dados não encontrado: {DB_PATH}")
        return False
    
    if not os.path.exists(MIGRATION_FILE):
        print(f"❌ Erro: Arquivo de migração não encontrado: {MIGRATION_FILE}")
        return False
    
    print("=" * 60)
    print("🔄 Aplicando Migração: Contextos de Field Locks")
    print("=" * 60)
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(field_locks)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'context' in columns:
            print("⚠️  Coluna 'context' já existe na tabela field_locks")
            
            # Verificar quantos registros existem por contexto
            cursor.execute("SELECT context, COUNT(*) FROM field_locks GROUP BY context")
            results = cursor.fetchall()
            
            print("\n📊 Registros atuais por contexto:")
            for context, count in results:
                print(f"   - {context}: {count} registros")
            
            response = input("\n🤔 Deseja recriar os registros de 'response'? (s/N): ")
            if response.lower() != 's':
                print("✅ Migração cancelada - banco já está atualizado")
                conn.close()
                return True
        
        # Ler o arquivo SQL
        with open(MIGRATION_FILE, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        print("\n📋 Executando migração...")
        
        # Executar o script SQL
        cursor.executescript(sql_script)
        
        # Verificar resultados
        cursor.execute("SELECT context, COUNT(*) FROM field_locks GROUP BY context")
        results = cursor.fetchall()
        
        print("\n✅ Migração aplicada com sucesso!")
        print("\n📊 Registros finais por contexto:")
        for context, count in results:
            emoji = "🆕" if context == "creation" else "📝"
            print(f"   {emoji} {context.upper()}: {count} registros")
        
        # Commit e fechar
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✨ Sistema agora suporta permissões separadas!")
        print("   🆕 CREATION - Permissões ao criar novo RNC")
        print("   📝 RESPONSE - Permissões ao responder/editar RNC")
        print("=" * 60)
        
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Erro ao aplicar migração: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return False

def rollback_migration():
    """Reverte a migração (remove coluna context)"""
    print("\n⚠️  ATENÇÃO: Isto irá remover a coluna 'context' e mesclar todas as permissões!")
    response = input("Deseja continuar? (s/N): ")
    
    if response.lower() != 's':
        print("✅ Rollback cancelado")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("\n🔄 Revertendo migração...")
        
        # SQLite não suporta DROP COLUMN diretamente, então precisamos recriar a tabela
        cursor.execute("""
            CREATE TABLE field_locks_backup AS
            SELECT DISTINCT group_id, field_name, is_locked, created_at, updated_at
            FROM field_locks
            WHERE context = 'creation'
        """)
        
        cursor.execute("DROP TABLE field_locks")
        cursor.execute("ALTER TABLE field_locks_backup RENAME TO field_locks")
        
        conn.commit()
        conn.close()
        
        print("✅ Migração revertida com sucesso!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erro ao reverter migração: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "🔐 " * 20)
    print("   MIGRAÇÃO: Sistema de Contextos para Field Locks")
    print("🔐 " * 20 + "\n")
    
    print("Opções:")
    print("  1. Aplicar migração (adicionar contextos)")
    print("  2. Reverter migração (remover contextos)")
    print("  3. Cancelar")
    
    choice = input("\nEscolha uma opção (1-3): ").strip()
    
    if choice == "1":
        success = apply_migration()
        exit(0 if success else 1)
    elif choice == "2":
        success = rollback_migration()
        exit(0 if success else 1)
    else:
        print("✅ Operação cancelada")
        exit(0)
