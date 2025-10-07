import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Atualizar RNC 62611 com dados de teste
cursor.execute("""
UPDATE rncs 
SET instruction_retrabalho = ?, 
    cause_rnc = ?, 
    action_rnc = ?
WHERE id = 62611
""", (
    "TESTE: Verificar dimensões da peça e refazer usinagem conforme desenho técnico", 
    "TESTE: Erro na fixação da peça durante usinagem causou desvio dimensional",
    "TESTE: Recalibrar dispositivos de fixação e retreinar operador responsável"
))

conn.commit()
rows_affected = cursor.rowcount

print(f"RNC 62611 atualizada. Linhas afetadas: {rows_affected}")

# Verificar se foi salvo
cursor.execute('SELECT id, rnc_number, instruction_retrabalho, cause_rnc, action_rnc FROM rncs WHERE id = 62611')
result = cursor.fetchone()

if result:
    print(f'\nVerificação:')
    print(f'ID: {result[0]}')
    print(f'RNC: {result[1]}')
    print(f'Instrução: {result[2]}')
    print(f'Causa: {result[3]}')
    print(f'Ação: {result[4]}')

conn.close()
