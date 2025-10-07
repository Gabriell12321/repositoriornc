import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Atualizar RNC 62611 com dados técnicos completos no campo description
description_completa = """Desenho: DES-001-2025
MP: Aço 1020
Revisão: Rev. 02
POS: POS-15
CV: CV-8547
Modelo: MOD-XYZ-123
Conjunto: CONJ-USINAGEM-01
Quantidade: 50 unidades
Material: Aço carbono 1020
OC: OC-2025-0828-001
Descrição da RNC: Dimensões fora da tolerância especificada no desenho técnico"""

cursor.execute("""
UPDATE rncs 
SET description = ?
WHERE id = 62611
""", (description_completa,))

conn.commit()
rows_affected = cursor.rowcount

print(f"RNC 62611 atualizada com dados técnicos. Linhas afetadas: {rows_affected}")

# Verificar se foi salvo
cursor.execute('SELECT id, rnc_number, title, description FROM rncs WHERE id = 62611')
result = cursor.fetchone()

if result:
    print(f'\nVerificação:')
    print(f'ID: {result[0]}')
    print(f'RNC: {result[1]}')
    print(f'Título: {result[2]}')
    print(f'Descrição:\n{result[3]}')

conn.close()
