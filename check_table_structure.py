import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

print("=== Estrutura da tabela rncs ===")
cursor.execute("PRAGMA table_info(rncs)")
columns = cursor.fetchall()
for col in columns:
    print(f"{col[0]}: {col[1]} ({col[2]})")

print("\n=== Total de RNCs ===")
cursor.execute("SELECT COUNT(*) FROM rncs WHERE (is_deleted = 0 OR is_deleted IS NULL)")
print(f"Total: {cursor.fetchone()[0]}")

print("\n=== RNCs de Engenharia ===")
try:
    cursor.execute("""
        SELECT COUNT(*) 
        FROM rncs 
        WHERE (
            LOWER(TRIM(area_responsavel)) LIKE '%engenharia%'
            OR LOWER(TRIM(setor)) LIKE '%engenharia%'
            OR LOWER(TRIM(signature_engineering_name)) LIKE '%engenharia%'
        )
        AND (is_deleted = 0 OR is_deleted IS NULL)
    """)
    print(f"Total Engenharia: {cursor.fetchone()[0]}")
except Exception as e:
    print(f"Erro: {e}")

conn.close()
