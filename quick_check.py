import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

print("=== Verificação Rápida de RNCs ===\n")

# Total
cursor.execute("SELECT COUNT(*) FROM rncs")
total = cursor.fetchone()[0]
print(f"Total de RNCs: {total}")

# Por status
cursor.execute("SELECT status, COUNT(*) FROM rncs GROUP BY status")
print("\nPor Status:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Finalizadas
cursor.execute("SELECT COUNT(*) FROM rncs WHERE status = 'Finalizado'")
finalizadas = cursor.fetchone()[0]
print(f"\nTotal Finalizadas: {finalizadas}")

# Com área responsável preenchida
cursor.execute("SELECT COUNT(*) FROM rncs WHERE area_responsavel IS NOT NULL AND area_responsavel != ''")
com_area = cursor.fetchone()[0]
print(f"Com área responsável: {com_area}")

conn.close()
