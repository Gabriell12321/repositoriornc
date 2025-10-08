import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

print("=== Verificando dados na tabela rncs ===")

# Total de registros (incluindo deletados)
cursor.execute("SELECT COUNT(*) FROM rncs")
total = cursor.fetchone()[0]
print(f"Total de registros (incluindo deletados): {total}")

# Registros não deletados
cursor.execute("SELECT COUNT(*) FROM rncs WHERE (is_deleted = 0 OR is_deleted IS NULL)")
not_deleted = cursor.fetchone()[0]
print(f"Registros não deletados: {not_deleted}")

# Registros deletados
cursor.execute("SELECT COUNT(*) FROM rncs WHERE is_deleted = 1")
deleted = cursor.fetchone()[0]
print(f"Registros deletados: {deleted}")

# Mostrar alguns registros se existirem
if total > 0:
    print("\n=== Primeiros 5 registros ===")
    cursor.execute("SELECT id, rnc_number, title, status, created_at FROM rncs LIMIT 5")
    for row in cursor.fetchall():
        print(row)

conn.close()
