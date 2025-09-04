import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

print("=== Estrutura da tabela rncs ===")
cursor.execute("PRAGMA table_info(rncs)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]} ({col[2]})")

print("\n=== Últimas 3 RNCs ===")
cursor.execute("SELECT * FROM rncs ORDER BY id DESC LIMIT 3")
rncs = cursor.fetchall()
for rnc in rncs:
    print(f"RNC ID: {rnc[0]}, Number: {rnc[1]}, Title: {rnc[2]}")
    print(f"  Equipment: {rnc[4]}, Client: {rnc[5]}")
    print(f"  Status: {rnc[7]}, Price: {rnc[13]}")
    print()

conn.close()
