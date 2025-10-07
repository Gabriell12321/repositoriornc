import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Verificar RNCs finalizadas da engenharia
cursor.execute("""
    SELECT COUNT(*) 
    FROM rncs 
    WHERE finalized_at IS NOT NULL 
    AND (
        responsavel LIKE '%guilherme%' OR 
        responsavel LIKE '%cintia%' OR 
        responsavel LIKE '%cíntia%' OR
        area_responsavel LIKE '%engenharia%' OR
        setor LIKE '%engenharia%' OR
        title LIKE '%engenharia%'
    ) 
    AND (is_deleted = 0 OR is_deleted IS NULL)
""")

total = cursor.fetchone()[0]
print(f"Total RNCs Engenharia Finalizadas: {total}")

# Ver alguns exemplos
cursor.execute("""
    SELECT id, rnc_number, title, responsavel, area_responsavel, setor, finalized_at
    FROM rncs 
    WHERE finalized_at IS NOT NULL 
    AND (
        responsavel LIKE '%guilherme%' OR 
        responsavel LIKE '%cintia%' OR 
        responsavel LIKE '%cíntia%' OR
        area_responsavel LIKE '%engenharia%' OR
        setor LIKE '%engenharia%' OR
        title LIKE '%engenharia%'
    ) 
    AND (is_deleted = 0 OR is_deleted IS NULL)
    LIMIT 5
""")

print("\nExemplos de RNCs:")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, N°: {row[1]}, Responsável: {row[3]}, Área: {row[4]}, Setor: {row[5]}")

conn.close()
