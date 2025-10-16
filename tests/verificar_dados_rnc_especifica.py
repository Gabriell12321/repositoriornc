import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Verificar uma RNC específica
cursor.execute("""
    SELECT id, signature_inspection_date, signature_engineering_date, signature_inspection2_date,
           disposition_usar, disposition_retrabalhar, disposition_rejeitar, disposition_sucata,
           disposition_devolver_estoque, disposition_devolver_fornecedor
    FROM rncs 
    WHERE id = 34415
""")

rnc = cursor.fetchone()
if rnc:
    print("RNC 34415:")
    print(f"  signature_inspection_date: '{rnc[1]}'")
    print(f"  signature_engineering_date: '{rnc[2]}'")
    print(f"  signature_inspection2_date: '{rnc[3]}'")
    print(f"  disposition_usar: {rnc[4]}")
    print(f"  disposition_retrabalhar: {rnc[5]}")
    print(f"  disposition_rejeitar: {rnc[6]}")
    print(f"  disposition_sucata: {rnc[7]}")
    print(f"  disposition_devolver_estoque: {rnc[8]}")
    print(f"  disposition_devolver_fornecedor: {rnc[9]}")

# Ver algumas outras RNCs
print("\n\nAmostras de outras RNCs:")
cursor.execute("""
    SELECT id, signature_inspection_date, disposition_retrabalhar
    FROM rncs 
    LIMIT 5
""")

for row in cursor.fetchall():
    print(f"RNC {row[0]}: data='{row[1]}', retrabalhar={row[2]}")

conn.close()
