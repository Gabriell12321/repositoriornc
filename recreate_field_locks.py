#!/usr/bin/env python3
"""
Script para recriar a tabela field_locks com a estrutura correta
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'ippel_system.db'

def recreate_field_locks_table():
    """Recria a tabela field_locks com estrutura correta"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("🔧 Recriando tabela field_locks")
        print("=" * 60)
        
        # 1. Fazer backup dos dados existentes
        print("\n1️⃣ Fazendo backup dos dados...")
        cursor.execute("SELECT * FROM field_locks")
        backup_data = cursor.fetchall()
        print(f"   ✅ {len(backup_data)} registros salvos em memória")
        
        # 2. Renomear tabela antiga
        print("\n2️⃣ Renomeando tabela antiga...")
        cursor.execute("ALTER TABLE field_locks RENAME TO field_locks_old")
        conn.commit()
        print("   ✅ Tabela renomeada para field_locks_old")
        
        # 3. Criar nova tabela com estrutura correta
        print("\n3️⃣ Criando nova tabela field_locks...")
        cursor.execute("""
            CREATE TABLE field_locks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                field_name TEXT NOT NULL,
                is_locked BOOLEAN DEFAULT 0,
                is_required BOOLEAN DEFAULT 0,
                context TEXT DEFAULT 'creation',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(group_id, field_name, context),
                FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        print("   ✅ Nova tabela criada com UNIQUE(group_id, field_name, context)")
        
        # 4. Criar índices
        print("\n4️⃣ Criando índices...")
        cursor.execute("CREATE INDEX idx_field_locks_context ON field_locks(context)")
        cursor.execute("CREATE INDEX idx_field_locks_group_context ON field_locks(group_id, context)")
        cursor.execute("CREATE INDEX idx_field_locks_field_name ON field_locks(field_name)")
        cursor.execute("CREATE INDEX idx_field_locks_group_id ON field_locks(group_id)")
        conn.commit()
        print("   ✅ Índices criados!")
        
        # 5. Restaurar dados
        print("\n5️⃣ Restaurando dados...")
        
        # Verificar se os dados já têm a coluna context
        cursor.execute("PRAGMA table_info(field_locks_old)")
        old_columns = [col[1] for col in cursor.fetchall()]
        has_context = 'context' in old_columns
        
        if has_context:
            # Dados já têm context, copiar diretamente
            cursor.execute("""
                INSERT INTO field_locks (id, group_id, field_name, is_locked, is_required, context, created_at, updated_at)
                SELECT id, group_id, field_name, is_locked, is_required, context, created_at, updated_at
                FROM field_locks_old
            """)
        else:
            # Dados não têm context, adicionar 'creation' como padrão
            cursor.execute("""
                INSERT INTO field_locks (id, group_id, field_name, is_locked, is_required, context, created_at, updated_at)
                SELECT id, group_id, field_name, is_locked, is_required, 'creation', created_at, updated_at
                FROM field_locks_old
            """)
            
            # Duplicar para 'response'
            cursor.execute("""
                INSERT INTO field_locks (group_id, field_name, is_locked, is_required, context, created_at, updated_at)
                SELECT group_id, field_name, is_locked, is_required, 'response', created_at, updated_at
                FROM field_locks_old
            """)
        
        conn.commit()
        
        # Verificar quantos registros foram restaurados
        cursor.execute("SELECT COUNT(*) FROM field_locks")
        new_count = cursor.fetchone()[0]
        print(f"   ✅ {new_count} registros restaurados")
        
        # 6. Verificar por contexto
        print("\n6️⃣ Verificando registros por contexto...")
        cursor.execute("SELECT context, COUNT(*) FROM field_locks GROUP BY context")
        for context, count in cursor.fetchall():
            print(f"   - {context}: {count} registros")
        
        # 7. Dropar tabela antiga
        print("\n7️⃣ Removendo tabela antiga...")
        cursor.execute("DROP TABLE field_locks_old")
        conn.commit()
        print("   ✅ Tabela antiga removida")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Tabela recriada com sucesso!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        
        # Tentar reverter
        try:
            cursor.execute("DROP TABLE IF EXISTS field_locks")
            cursor.execute("ALTER TABLE field_locks_old RENAME TO field_locks")
            conn.commit()
            print("\n⚠️  Mudanças revertidas!")
        except:
            pass
        
        return False

if __name__ == "__main__":
    print("\n" + "🔐 " * 20)
    print("   RECRIAR TABELA: field_locks")
    print("🔐 " * 20 + "\n")
    
    print("⚠️  ATENÇÃO: Este script irá recriar a tabela field_locks!")
    print("   - Backup dos dados será feito automaticamente")
    print("   - A tabela será recriada com a estrutura correta")
    print("   - Registros serão duplicados para contextos creation/response")
    print()
    
    response = input("Deseja continuar? (s/N): ")
    
    if response.lower() == 's':
        success = recreate_field_locks_table()
        if success:
            print("\n🎉 Operação concluída com sucesso!")
            print("   Agora você pode usar o sistema de permissões normalmente.")
    else:
        print("\n❌ Operação cancelada")
