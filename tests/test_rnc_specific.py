import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Verificar RNC específica
cursor.execute('SELECT id, rnc_number, title, description, equipment, client, instruction_retrabalho, cause_rnc, action_rnc FROM rncs WHERE id = 62611')
result = cursor.fetchone()

if result:
    print(f'RNC ID: {result[0]}')
    print(f'Número: {result[1]}')
    print(f'Título: {result[2]}')
    print(f'Descrição: {result[3]}')
    print(f'Equipamento: {result[4]}')
    print(f'Cliente: {result[5]}')
    print(f'Instrução: {result[6]}')
    print(f'Causa: {result[7]}')
    print(f'Ação: {result[8]}')
else:
    print('RNC não encontrada')

conn.close()
