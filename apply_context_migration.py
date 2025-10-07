"""
Script para aplicar migração: adicionar contexto às permissões de campos
Adiciona coluna 'context' para diferenciar permissões de CRIAÇÃO e RESPOSTA
Executar: python apply_context_migration.py
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'ippel_system.db')

def apply_migration():
    print("🔄 Iniciando migração: Adicionar contexto às permissões...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(field_locks)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'context' in columns:
            print("⚠️  Coluna 'context' já existe. Pulando migração.")
            conn.close()
            return
        
        print("📝 Adicionando coluna 'context'...")
        cursor.execute("ALTER TABLE field_locks ADD COLUMN context TEXT DEFAULT 'creation'")
        
        print("📝 Criando índice para performance...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_field_locks_context ON field_locks(group_id, context)")
        
        print("📝 Duplicando registros existentes para contexto 'response'...")
        cursor.execute("""
            INSERT INTO field_locks (group_id, field_name, is_locked, context, created_at, updated_at)
            SELECT group_id, field_name, is_locked, 'response', created_at, datetime('now')
            FROM field_locks
            WHERE context = 'creation'
        """)
        
        rows_affected = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"✅ Migração concluída com sucesso!")
        print(f"   - Coluna 'context' adicionada")
        print(f"   - Índice criado")
        print(f"   - {rows_affected} registros duplicados para contexto 'response'")
        print(f"\n🎯 Agora você tem permissões separadas para CRIAÇÃO e RESPOSTA de RNCs!")
        
    except Exception as e:
        print(f"❌ Erro ao aplicar migração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    apply_migration()
