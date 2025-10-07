import sqlite3

# Conectar ao banco
conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Obter estrutura da tabela RNC
cursor.execute("PRAGMA table_info(rnc)")
columns = cursor.fetchall()

print("=== CAMPOS DA TABELA RNC ===")
print("Total de campos:", len(columns))
print()

for col in columns:
    cid, name, type_, notnull, default, pk = col
    print(f"{name:<25} | {type_:<15} | {'NOT NULL' if notnull else 'NULL':<8} | {'PK' if pk else ''}")

conn.close()