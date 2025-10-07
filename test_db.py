import sqlite3

try:
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Listar tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"✅ Banco OK - {len(tables)} tabelas encontradas")
    print(f"Tabelas: {', '.join(tables)}")
    
    # Verificar field_locks
    if 'field_locks' in tables:
        cursor.execute("PRAGMA table_info(field_locks)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"\nColunas em field_locks: {', '.join(columns)}")
        
        if 'context' in columns:
            print("✅ Coluna 'context' JÁ EXISTE!")
            cursor.execute("SELECT context, COUNT(*) FROM field_locks GROUP BY context")
            for ctx, cnt in cursor.fetchall():
                print(f"  - {ctx}: {cnt} registros")
        else:
            print("⚠️  Coluna 'context' NÃO EXISTE - migração necessária")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")
