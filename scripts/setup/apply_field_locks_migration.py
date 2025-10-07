import sqlite3
import os

def apply_migration():
    """Aplica a migração do sistema de bloqueio de campos"""
    db_path = 'ippel_system.db'
    migration_path = os.path.join('migrations', 'create_field_locks_enhanced.sql')
    
    print("🔄 Aplicando migração do sistema de bloqueio de campos...")
    
    try:
        # Ler o arquivo de migração
        with open(migration_path, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Executar a migração
        cursor.executescript(migration_sql)
        conn.commit()
        
        # Verificar se a tabela foi criada
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='field_locks'")
        table_exists = cursor.fetchone()[0] > 0
        
        if table_exists:
            # Contar registros criados
            cursor.execute("SELECT COUNT(*) FROM field_locks")
            total_records = cursor.fetchone()[0]
            
            # Contar grupos afetados
            cursor.execute("SELECT COUNT(DISTINCT group_id) FROM field_locks")
            groups_count = cursor.fetchone()[0]
            
            print(f"✅ Migração aplicada com sucesso!")
            print(f"📊 Tabela field_locks criada")
            print(f"📝 {total_records} configurações de campo criadas")
            print(f"👥 {groups_count} grupos configurados")
            
            # Mostrar grupos configurados
            cursor.execute("""
                SELECT g.name, COUNT(fl.id) as campos_configurados
                FROM groups g
                LEFT JOIN field_locks fl ON g.id = fl.group_id
                GROUP BY g.id, g.name
                ORDER BY g.name
            """)
            groups_info = cursor.fetchall()
            
            print("\n📋 Grupos configurados:")
            for group_name, field_count in groups_info:
                print(f"   • {group_name}: {field_count} campos")
                
        else:
            print("❌ Erro: Tabela field_locks não foi criada")
            
        conn.close()
        
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo de migração não encontrado: {migration_path}")
    except sqlite3.Error as e:
        print(f"❌ Erro de banco de dados: {e}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    apply_migration()