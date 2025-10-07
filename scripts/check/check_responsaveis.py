import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Ver todos os responsáveis únicos em RNCs finalizadas
print("=== RESPONSÁVEIS únicos nas RNCs finalizadas ===")
cursor.execute("""
    SELECT DISTINCT responsavel, COUNT(*) as total
    FROM rncs 
    WHERE finalized_at IS NOT NULL 
    AND (is_deleted = 0 OR is_deleted IS NULL)
    GROUP BY responsavel
    ORDER BY total DESC
    LIMIT 10
""")
for row in cursor.fetchall():
    print(f"{row[1]:4d} RNCs - Responsável: '{row[0]}'")

print("\n=== ÁREAS RESPONSÁVEIS únicas nas RNCs finalizadas ===")
cursor.execute("""
    SELECT DISTINCT area_responsavel, COUNT(*) as total
    FROM rncs 
    WHERE finalized_at IS NOT NULL 
    AND (is_deleted = 0 OR is_deleted IS NULL)
    GROUP BY area_responsavel
    ORDER BY total DESC
    LIMIT 10
""")
for row in cursor.fetchall():
    print(f"{row[1]:4d} RNCs - Área: '{row[0]}'")

print("\n=== SETORES únicos nas RNCs finalizadas ===")
cursor.execute("""
    SELECT DISTINCT setor, COUNT(*) as total
    FROM rncs 
    WHERE finalized_at IS NOT NULL 
    AND (is_deleted = 0 OR is_deleted IS NULL)
    GROUP BY setor
    ORDER BY total DESC
    LIMIT 10
""")
for row in cursor.fetchall():
    print(f"{row[1]:4d} RNCs - Setor: '{row[0]}'")

print("\n=== Total de RNCs finalizadas ===")
cursor.execute("SELECT COUNT(*) FROM rncs WHERE finalized_at IS NOT NULL AND (is_deleted = 0 OR is_deleted IS NULL)")
print(f"Total: {cursor.fetchone()[0]} RNCs finalizadas")

conn.close()
