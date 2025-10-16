import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Verificar RNCs finalizadas da engenharia com o novo critério
cursor.execute("""
    SELECT COUNT(*) 
    FROM rncs 
    WHERE status = 'Finalizado'
    AND area_responsavel = 'Engenharia'
    AND (is_deleted = 0 OR is_deleted IS NULL)
""")

total = cursor.fetchone()[0]
print(f"Total RNCs Engenharia Finalizadas (status='Finalizado' + área='Engenharia'): {total}")

# Ver alguns exemplos
cursor.execute("""
    SELECT id, rnc_number, title, responsavel, area_responsavel, status
    FROM rncs 
    WHERE status = 'Finalizado'
    AND area_responsavel = 'Engenharia'
    AND (is_deleted = 0 OR is_deleted IS NULL)
    LIMIT 10
""")

print("\nExemplos de RNCs da Engenharia:")
for row in cursor.fetchall():
    print(f"ID: {row[0]}, N°: {row[1]}, Responsável: {row[3]}, Status: {row[5]}")

conn.close()
