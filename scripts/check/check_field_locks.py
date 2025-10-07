import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='field_locks'")
exists = bool(cursor.fetchone())
print(f"field_locks table exists: {exists}")

if not exists:
    print("Precisa criar a tabela field_locks")
else:
    print("Tabela field_locks já existe")

conn.close()