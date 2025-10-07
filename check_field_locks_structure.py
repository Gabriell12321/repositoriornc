import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

print("=== ESTRUTURA DA TABELA field_locks ===")
cursor.execute('PRAGMA table_info(field_locks)')
for row in cursor.fetchall():
    print(row)

print("\n=== ÍNDICES ===")
cursor.execute("SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='field_locks'")
for row in cursor.fetchall():
    print(row[0] if row[0] else "NULL")

print("\n=== CONSTRAINTS ===")
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='field_locks'")
result = cursor.fetchone()
if result:
    print(result[0])

conn.close()
