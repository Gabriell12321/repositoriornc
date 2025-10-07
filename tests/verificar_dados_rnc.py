import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Total de RNCs
cursor.execute('SELECT COUNT(*) FROM rncs')
total = cursor.fetchone()[0]

# RNCs com campos preenchidos
cursor.execute("SELECT COUNT(*) FROM rncs WHERE cause_rnc IS NOT NULL AND cause_rnc != ''")
com_causa = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM rncs WHERE action_rnc IS NOT NULL AND action_rnc != ''")
com_acao = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM rncs WHERE justificativa IS NOT NULL AND justificativa != ''")
com_justif = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM rncs WHERE instruction_retrabalho IS NOT NULL AND instruction_retrabalho != ''")
com_instrucao = cursor.fetchone()[0]

# RNCs com assinaturas
cursor.execute("SELECT COUNT(*) FROM rncs WHERE signature_inspection_name IS NOT NULL AND signature_inspection_name != ''")
com_assinatura = cursor.fetchone()[0]

# RNCs com disposição marcada
cursor.execute("SELECT COUNT(*) FROM rncs WHERE disposition_usar = 1 OR disposition_retrabalhar = 1 OR disposition_rejeitar = 1 OR disposition_sucata = 1 OR disposition_devolver_estoque = 1 OR disposition_devolver_fornecedor = 1")
com_disposicao = cursor.fetchone()[0]

print(f'📊 ESTATÍSTICAS DO BANCO DE DADOS')
print(f'=' * 50)
print(f'Total de RNCs: {total}')
print(f'')
print(f'RNCs com Instrução para Retrabalho: {com_instrucao} ({com_instrucao*100/total:.1f}%)')
print(f'RNCs com Causa da RNC: {com_causa} ({com_causa*100/total:.1f}%)')
print(f'RNCs com Ação a ser Tomada: {com_acao} ({com_acao*100/total:.1f}%)')
print(f'RNCs com Justificativa: {com_justif} ({com_justif*100/total:.1f}%)')
print(f'RNCs com Assinaturas: {com_assinatura} ({com_assinatura*100/total:.1f}%)')
print(f'RNCs com Disposição: {com_disposicao} ({com_disposicao*100/total:.1f}%)')
print(f'')

# Exemplos de RNCs com e sem dados
print(f'📋 EXEMPLOS DE RNCs SEM DADOS:')
cursor.execute("SELECT id, rnc_number FROM rncs WHERE (cause_rnc IS NULL OR cause_rnc = '') AND (action_rnc IS NULL OR action_rnc = '') LIMIT 5")
sem_dados = cursor.fetchall()
for rnc in sem_dados:
    print(f'  - RNC {rnc[1]} (ID: {rnc[0]})')

print(f'')
print(f'✅ EXEMPLOS DE RNCs COM DADOS:')
cursor.execute("SELECT id, rnc_number FROM rncs WHERE cause_rnc IS NOT NULL AND cause_rnc != '' LIMIT 5")
com_dados = cursor.fetchall()
for rnc in com_dados:
    print(f'  - RNC {rnc[1]} (ID: {rnc[0]})')

conn.close()
