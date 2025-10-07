import sqlite3

# Conectar ao banco
conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Listar todas as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print("=== TABELAS DO BANCO ===")
for table in tables:
    print(f"  - {table[0]}")

# Verificar se tem tabela rncs (plural)
print("\n=== VERIFICANDO TABELA RNCS ===")
try:
    cursor.execute("PRAGMA table_info(rncs)")
    columns = cursor.fetchall()
    
    print(f"Total de campos: {len(columns)}")
    print()
    
    for col in columns:
        cid, name, type_, notnull, default, pk = col
        print(f"{name:<30} | {type_:<15} | {'NOT NULL' if notnull else 'NULL':<8} | {'PK' if pk else ''}")
        
except Exception as e:
    print(f"Erro: {e}")

conn.close()