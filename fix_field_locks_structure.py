#!/usr/bin/env python3
"""
Script para verificar e corrigir a estrutura da tabela field_locks
"""

import sqlite3
import os

DB_PATH = 'ippel_system.db'

def check_field_locks_structure():
    """Verifica a estrutura da tabela field_locks"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("🔍 Verificando estrutura da tabela field_locks")
        print("=" * 60)
        
        # Verificar colunas
        cursor.execute("PRAGMA table_info(field_locks)")
        columns = cursor.fetchall()
        
        print("\n📋 Colunas existentes:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # Verificar índices
        cursor.execute("PRAGMA index_list(field_locks)")
        indexes = cursor.fetchall()
        
        print("\n🔑 Índices existentes:")
        for idx in indexes:
            idx_name = idx[1]
            print(f"\n  Índice: {idx_name}")
            cursor.execute(f"PRAGMA index_info({idx_name})")
            idx_cols = cursor.fetchall()
            for col_info in idx_cols:
                print(f"    - Coluna: {col_info[2]}")
        
        # Verificar se existe constraint único com context
        has_context_constraint = False
        for idx in indexes:
            if idx[2] == 1:  # unique index
                cursor.execute(f"PRAGMA index_info({idx[1]})")
                idx_cols = [c[2] for c in cursor.fetchall()]
                if 'context' in idx_cols:
                    has_context_constraint = True
                    print(f"\n✅ Constraint único com context encontrado: {idx[1]}")
                    print(f"   Colunas: {', '.join(idx_cols)}")
        
        if not has_context_constraint:
            print("\n⚠️  PROBLEMA: Não existe constraint único que inclui 'context'")
            print("   Isso causa erro no INSERT ... ON CONFLICT")
        
        conn.close()
        return has_context_constraint
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return False

def fix_field_locks_structure():
    """Corrige a estrutura adicionando constraint único correto"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("\n" + "=" * 60)
        print("🔧 Corrigindo estrutura da tabela field_locks")
        print("=" * 60)
        
        # Verificar se já existe a coluna context
        cursor.execute("PRAGMA table_info(field_locks)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'context' not in columns:
            print("\n1️⃣ Adicionando coluna 'context'...")
            cursor.execute("ALTER TABLE field_locks ADD COLUMN context TEXT DEFAULT 'creation'")
            conn.commit()
            print("   ✅ Coluna adicionada!")
        else:
            print("\n1️⃣ Coluna 'context' já existe")
        
        # Remover índice único antigo se existir
        print("\n2️⃣ Removendo índices antigos...")
        cursor.execute("PRAGMA index_list(field_locks)")
        for idx in cursor.fetchall():
            if idx[2] == 1:  # unique index
                idx_name = idx[1]
                print(f"   Removendo: {idx_name}")
                cursor.execute(f"DROP INDEX IF EXISTS {idx_name}")
        
        # Criar novo índice único com context
        print("\n3️⃣ Criando novo índice único (group_id, field_name, context)...")
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_group_field_context 
            ON field_locks(group_id, field_name, context)
        """)
        conn.commit()
        print("   ✅ Índice criado!")
        
        # Criar índices para performance
        print("\n4️⃣ Criando índices adicionais...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_field_locks_context ON field_locks(context)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_field_locks_group_context ON field_locks(group_id, context)")
        conn.commit()
        print("   ✅ Índices criados!")
        
        # Duplicar registros para contexto 'response' se necessário
        print("\n5️⃣ Verificando registros...")
        cursor.execute("SELECT COUNT(*) FROM field_locks WHERE context = 'response'")
        response_count = cursor.fetchone()[0]
        
        if response_count == 0:
            print("   Duplicando registros para contexto 'response'...")
            cursor.execute("""
                INSERT OR IGNORE INTO field_locks (group_id, field_name, is_locked, context, created_at, updated_at)
                SELECT group_id, field_name, is_locked, 'response', created_at, updated_at
                FROM field_locks
                WHERE context = 'creation'
            """)
            conn.commit()
            print(f"   ✅ {cursor.rowcount} registros duplicados!")
        else:
            print(f"   ✅ Já existem {response_count} registros para 'response'")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Estrutura corrigida com sucesso!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao corrigir: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "🔐 " * 20)
    print("   VERIFICAÇÃO E CORREÇÃO: Tabela field_locks")
    print("🔐 " * 20 + "\n")
    
    # Verificar estrutura atual
    has_correct_structure = check_field_locks_structure()
    
    if not has_correct_structure:
        print("\n⚠️  Estrutura precisa ser corrigida!")
        response = input("\nDeseja corrigir agora? (s/N): ")
        
        if response.lower() == 's':
            success = fix_field_locks_structure()
            
            if success:
                print("\n🎉 Correção concluída! Verifique novamente:")
                check_field_locks_structure()
        else:
            print("\n❌ Correção cancelada")
    else:
        print("\n✅ Estrutura está correta!")
