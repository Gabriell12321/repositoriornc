import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Verificar últimas RNCs
cursor.execute('SELECT id, rnc_number, title, equipment, client, instruction_retrabalho, cause_rnc, action_rnc FROM rncs ORDER BY id DESC LIMIT 3')
results = cursor.fetchall()

print('=== ÚLTIMAS 3 RNCs ===')
for row in results:
    print(f'ID: {row[0]}, RNC: {row[1]}, Título: {row[2]}')
    print(f'  Equipamento: {row[3]}')
    print(f'  Cliente: {row[4]}')
    print(f'  Instrução: {row[5]}')
    print(f'  Causa: {row[6]}')
    print(f'  Ação: {row[7]}')
    print('---')

conn.close()
