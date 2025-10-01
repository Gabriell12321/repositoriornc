import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Verifica a RNC específica da imagem
cursor.execute('''SELECT id, rnc_number, title, instruction_retrabalho, cause_rnc, action_rnc, description
                  FROM rncs WHERE rnc_number = 'RNC-2025-08-28-102946' ''')
result = cursor.fetchone()

if result:
    print(f'RNC encontrada: {result[1]}')
    print(f'Título: {result[2]}')
    print(f'Instrução: {result[3] or "(vazio)"}')
    print(f'Causa: {result[4] or "(vazio)"}')
    print(f'Ação: {result[5] or "(vazio)"}')
    print(f'Descrição (primeiros 200 chars): {(result[6] or "")[:200]}...')
else:
    print('RNC não encontrada')

conn.close()
