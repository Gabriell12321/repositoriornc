#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir a constraint UNIQUE da tabela field_locks
"""

import sqlite3
import sys

DB_PATH = 'ippel_system.db'

def fix_field_locks_constraint():
    """Corrige a constraint UNIQUE para incluir context"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("🔧 CORRIGINDO CONSTRAINT UNIQUE DA TABELA field_locks")
        print("=" * 60)
        
        # Verificar estrutura atual
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='field_locks'")
        current_schema = cursor.fetchone()
        
        print("\n📋 Esquema atual:")
        print(current_schema[0] if current_schema else "Tabela não encontrada")
        
        # Verificar se já tem a constraint correta
        if current_schema and 'UNIQUE(group_id, field_name, context)' in current_schema[0]:
            print("\n✅ Constraint já está correta!")
            conn.close()
            return True
        
        print("\n⚠️  Constraint precisa ser corrigida!")
        print("   Atual: UNIQUE(group_id, field_name)")
        print("   Necessária: UNIQUE(group_id, field_name, context)")
        
        # Backup dos dados
        print("\n💾 Fazendo backup dos dados...")
        cursor.execute("SELECT * FROM field_locks")
        backup_data = cursor.fetchall()
        print(f"   ✅ {len(backup_data)} registros salvos em memória")
        
        # Dropar a tabela antiga
        print("\n🗑️  Removendo tabela antiga...")
        cursor.execute("DROP TABLE field_locks")
        
        # Criar tabela nova com constraint correta
        print("\n🔨 Criando nova tabela com constraint correta...")
        cursor.execute("""
            CREATE TABLE field_locks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                field_name TEXT NOT NULL,
                is_locked BOOLEAN DEFAULT 0,
                is_required BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                context TEXT DEFAULT 'creation',
                FOREIGN KEY (group_id) REFERENCES groups(id),
                UNIQUE(group_id, field_name, context)
            )
        """)
        
        # Criar índices
        print("📊 Criando índices...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_field_locks_group_id ON field_locks(group_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_field_locks_field_name ON field_locks(field_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_field_locks_context ON field_locks(context)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_field_locks_group_field_context ON field_locks(group_id, field_name, context)")
        
        # Restaurar dados
        print(f"\n♻️  Restaurando {len(backup_data)} registros...")
        for row in backup_data:
            # row = (id, group_id, field_name, is_locked, is_required, created_at, updated_at, context)
            # Ignorar o ID antigo (deixar auto-incrementar)
            try:
                context = row[7] if len(row) > 7 and row[7] else 'creation'
                cursor.execute("""
                    INSERT INTO field_locks (group_id, field_name, is_locked, is_required, created_at, updated_at, context)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (row[1], row[2], row[3], row[4] if len(row) > 4 else 0, row[5] if len(row) > 5 else None, row[6] if len(row) > 6 else None, context))
            except Exception as e:
                print(f"   ⚠️  Erro ao restaurar registro: {e}")
        
        # Commit
        conn.commit()
        
        # Verificar resultado
        cursor.execute("SELECT COUNT(*) FROM field_locks")
        total = cursor.fetchone()[0]
        
        print(f"\n✅ {total} registros restaurados com sucesso!")
        
        # Verificar nova estrutura
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='field_locks'")
        new_schema = cursor.fetchone()
        
        print("\n📋 Novo esquema:")
        print(new_schema[0] if new_schema else "Erro ao verificar")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ CORREÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_field_locks_constraint()
    sys.exit(0 if success else 1)
