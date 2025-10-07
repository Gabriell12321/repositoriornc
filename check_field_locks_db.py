#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar e corrigir a estrutura da tabela field_locks
"""

import sqlite3
import sys

DB_PATH = 'ippel_system.db'

def check_database():
    """Verifica a estrutura da tabela field_locks"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("🔍 VERIFICANDO ESTRUTURA DA TABELA field_locks")
        print("=" * 60)
        
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='field_locks'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("❌ ERRO: Tabela 'field_locks' não existe!")
            print("\n✅ CRIANDO TABELA...")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS field_locks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    field_name TEXT NOT NULL,
                    is_locked BOOLEAN DEFAULT 0,
                    context TEXT DEFAULT 'creation',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (group_id) REFERENCES groups(id),
                    UNIQUE(group_id, field_name, context)
                )
            """)
            
            # Criar índices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_field_locks_group ON field_locks(group_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_field_locks_field ON field_locks(field_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_field_locks_context ON field_locks(context)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_field_locks_group_field_context ON field_locks(group_id, field_name, context)")
            
            conn.commit()
            print("✅ Tabela 'field_locks' criada com sucesso!")
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(field_locks)")
        columns = cursor.fetchall()
        
        print(f"\n📋 Estrutura da tabela 'field_locks':")
        print("-" * 60)
        for col in columns:
            print(f"  {col[1]:20} | {col[2]:15} | {'NOT NULL' if col[3] else 'NULL':8} | {'PK' if col[5] else ''}")
        
        # Verificar se coluna 'context' existe
        column_names = [col[1] for col in columns]
        
        if 'context' not in column_names:
            print("\n⚠️  ALERTA: Coluna 'context' não existe!")
            print("✅ ADICIONANDO COLUNA 'context'...")
            
            cursor.execute("ALTER TABLE field_locks ADD COLUMN context TEXT DEFAULT 'creation'")
            
            # Criar índice para context
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_field_locks_context ON field_locks(context)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_field_locks_group_field_context ON field_locks(group_id, field_name, context)")
            
            conn.commit()
            print("✅ Coluna 'context' adicionada com sucesso!")
        else:
            print("\n✅ Coluna 'context' já existe!")
        
        # Verificar registros existentes
        cursor.execute("SELECT COUNT(*) FROM field_locks")
        total_records = cursor.fetchone()[0]
        
        print(f"\n📊 Total de registros: {total_records}")
        
        if total_records > 0:
            # Verificar contextos
            cursor.execute("SELECT context, COUNT(*) FROM field_locks GROUP BY context")
            contexts = cursor.fetchall()
            print("\n📋 Registros por contexto:")
            for ctx, count in contexts:
                print(f"  {ctx or '(null)':15} | {count:5} registros")
            
            # Corrigir registros com context NULL
            cursor.execute("UPDATE field_locks SET context = 'creation' WHERE context IS NULL")
            updated = cursor.rowcount
            if updated > 0:
                conn.commit()
                print(f"\n✅ {updated} registros atualizados com context='creation'")
        
        # Verificar índices
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='field_locks'")
        indexes = cursor.fetchall()
        
        print(f"\n🔍 Índices da tabela ({len(indexes)} encontrados):")
        for idx in indexes:
            print(f"  - {idx[0]}")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ VERIFICAÇÃO CONCLUÍDA!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = check_database()
    sys.exit(0 if success else 1)
