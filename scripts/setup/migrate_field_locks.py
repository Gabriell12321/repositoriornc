"""
Migração: Sistema de Bloqueio de Campos por Grupo
Criado em: 03/10/2025

Este script cria a tabela field_locks e estrutura necessária
para o sistema de bloqueio de campos na criação de RNC.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'ippel_system.db'

def apply_migration():
    """Aplica a migração do sistema de bloqueio de campos"""
    
    print("=" * 70)
    print("MIGRAÇÃO: Sistema de Bloqueio de Campos por Grupo")
    print("=" * 70)
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Banco: {DB_PATH}")
    print()
    
    if not os.path.exists(DB_PATH):
        print(f"❌ ERRO: Banco de dados não encontrado: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("📋 Verificando estrutura atual...")
        
        # Verificar se a tabela já existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='field_locks'
        """)
        
        if cursor.fetchone():
            print("⚠️  Tabela 'field_locks' já existe!")
            resposta = input("   Deseja recriar? (s/N): ").strip().lower()
            if resposta != 's':
                print("❌ Migração cancelada pelo usuário.")
                conn.close()
                return False
            
            print("🗑️  Removendo tabela antiga...")
            cursor.execute("DROP TABLE IF EXISTS field_locks")
        
        # Criar tabela field_locks
        print("\n📦 Criando tabela 'field_locks'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS field_locks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                field_name TEXT NOT NULL,
                is_locked INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
                UNIQUE(group_id, field_name)
            )
        """)
        print("   ✅ Tabela criada!")
        
        # Criar índices
        print("\n🔍 Criando índices...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_field_locks_group 
            ON field_locks(group_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_field_locks_field 
            ON field_locks(field_name)
        """)
        print("   ✅ Índices criados!")
        
        # Criar trigger
        print("\n⚙️  Criando trigger de atualização...")
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_field_locks_timestamp 
            AFTER UPDATE ON field_locks
            BEGIN
                UPDATE field_locks 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END
        """)
        print("   ✅ Trigger criado!")
        
        # Listar grupos existentes
        print("\n👥 Grupos existentes no sistema:")
        cursor.execute("SELECT id, name FROM groups ORDER BY id")
        groups = cursor.fetchall()
        
        if not groups:
            print("   ⚠️  Nenhum grupo encontrado!")
        else:
            for group in groups:
                print(f"   • ID {group[0]}: {group[1]}")
        
        # Perguntar se deseja adicionar bloqueios iniciais
        print("\n" + "=" * 70)
        print("CONFIGURAÇÃO INICIAL (OPCIONAL)")
        print("=" * 70)
        
        if groups:
            add_initial = input("\nDeseja adicionar bloqueios iniciais para algum grupo? (s/N): ").strip().lower()
            
            if add_initial == 's':
                # Campos disponíveis para bloqueio
                available_fields = [
                    'title', 'description', 'equipment', 'client', 
                    'priority', 'status', 'responsavel', 'inspetor',
                    'setor', 'area_responsavel', 'price', 'assigned_user_id'
                ]
                
                print("\n📋 Campos disponíveis para bloqueio:")
                for i, field in enumerate(available_fields, 1):
                    print(f"   {i:2d}. {field}")
                
                print("\nExemplo de configuração:")
                print("  Para bloquear 'price' e 'priority' do grupo ID 2:")
                print("  Digite: 2:price,priority")
                print("\n  Para múltiplos grupos, separe por ponto-e-vírgula:")
                print("  Digite: 2:price,priority;3:status,price")
                print()
                
                config = input("Configuração (ou Enter para pular): ").strip()
                
                if config:
                    try:
                        # Parse configuração: grupo_id:campo1,campo2;grupo_id:campo3
                        for group_config in config.split(';'):
                            if ':' not in group_config:
                                continue
                            
                            group_id, fields = group_config.split(':', 1)
                            group_id = int(group_id.strip())
                            fields_list = [f.strip() for f in fields.split(',')]
                            
                            for field in fields_list:
                                if field in available_fields:
                                    cursor.execute("""
                                        INSERT OR REPLACE INTO field_locks 
                                        (group_id, field_name, is_locked)
                                        VALUES (?, ?, 1)
                                    """, (group_id, field))
                                    print(f"   ✅ Bloqueado '{field}' para grupo ID {group_id}")
                                else:
                                    print(f"   ⚠️  Campo inválido ignorado: '{field}'")
                    
                    except Exception as e:
                        print(f"   ⚠️  Erro ao processar configuração: {e}")
                        print("   Continuando sem bloqueios iniciais...")
        
        # Commit das mudanças
        conn.commit()
        
        # Verificar resultado
        print("\n" + "=" * 70)
        print("RESULTADO")
        print("=" * 70)
        
        cursor.execute("SELECT COUNT(*) FROM field_locks")
        count = cursor.fetchone()[0]
        print(f"✅ Migração aplicada com sucesso!")
        print(f"📊 Total de bloqueios configurados: {count}")
        
        if count > 0:
            print("\n📋 Bloqueios atuais:")
            cursor.execute("""
                SELECT g.name, fl.field_name, fl.is_locked
                FROM field_locks fl
                JOIN groups g ON fl.group_id = g.id
                ORDER BY g.name, fl.field_name
            """)
            for row in cursor.fetchall():
                status = "🔒 Bloqueado" if row[2] else "🔓 Liberado"
                print(f"   • {row[0]}: {row[1]} - {status}")
        
        print("\n💡 Próximos passos:")
        print("   1. Acesse /admin/field-locks para configurar bloqueios")
        print("   2. Teste criando RNC com usuários de diferentes grupos")
        print()
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO ao aplicar migração: {e}")
        import traceback
        traceback.print_exc()
        return False


def rollback_migration():
    """Remove a tabela field_locks (rollback)"""
    
    print("=" * 70)
    print("ROLLBACK: Remover Sistema de Bloqueio de Campos")
    print("=" * 70)
    
    resposta = input("⚠️  ATENÇÃO: Isso removerá TODOS os bloqueios configurados!\nContinuar? (s/N): ").strip().lower()
    
    if resposta != 's':
        print("❌ Rollback cancelado.")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("\n🗑️  Removendo trigger...")
        cursor.execute("DROP TRIGGER IF EXISTS update_field_locks_timestamp")
        
        print("🗑️  Removendo índices...")
        cursor.execute("DROP INDEX IF EXISTS idx_field_locks_group")
        cursor.execute("DROP INDEX IF EXISTS idx_field_locks_field")
        
        print("🗑️  Removendo tabela...")
        cursor.execute("DROP TABLE IF EXISTS field_locks")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Rollback concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO ao fazer rollback: {e}")
        return False


if __name__ == '__main__':
    print("\n🔧 MIGRAÇÃO DO BANCO DE DADOS")
    print("=" * 70)
    print("1. Aplicar migração (criar sistema de bloqueio)")
    print("2. Rollback (remover sistema de bloqueio)")
    print("3. Sair")
    print("=" * 70)
    
    escolha = input("\nEscolha uma opção (1-3): ").strip()
    
    if escolha == '1':
        apply_migration()
    elif escolha == '2':
        rollback_migration()
    else:
        print("Operação cancelada.")
