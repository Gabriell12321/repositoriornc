import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Verificar RNC específica
cursor.execute('''
    SELECT id, rnc_number, title, equipment, instruction_retrabalho, cause_rnc, action_rnc 
    FROM rncs 
    WHERE rnc_number = 'RNC-2025-08-28-104553'
''')
row = cursor.fetchone()

if row:
    print('=== DADOS DA RNC ===')
    print(f'ID: {row[0]}')
    print(f'RNC: {row[1]}')
    print(f'Title: {row[2]}')
    print(f'Equipment: {row[3]}')
    print(f'Instruction: {row[4]}')
    print(f'Cause: {row[5]}')
    print(f'Action: {row[6]}')
else:
    print('RNC não encontrada')

conn.close()
