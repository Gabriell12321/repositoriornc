import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Verificar RNC específica com todos os campos relevantes
cursor.execute('''
    SELECT id, rnc_number, title, equipment, instruction_retrabalho, cause_rnc, action_rnc, 
           signature_engineering_name, signature_inspection2_name, signature_inspection_name
    FROM rncs 
    WHERE rnc_number = 'RNC-2025-08-28-104553'
''')
row = cursor.fetchone()

if row:
    print('=== DADOS COMPLETOS DA RNC ===')
    print(f'ID: {row[0]}')
    print(f'RNC: {row[1]}')
    print(f'Title: {row[2]}')
    print(f'Equipment: {row[3]}')
    print(f'Instruction: {row[4]}')
    print(f'Cause: {row[5]}')
    print(f'Action: {row[6]}')
    print(f'Signature Engineering: {row[7]}')
    print(f'Signature Inspection2: {row[8]}')
    print(f'Signature Inspection: {row[9]}')
    
    print('\n=== ANÁLISE DOS PROBLEMAS ===')
    
    # Verificar campos que aparecem como "NOME" na imagem
    if row[7] == 'NOME':
        print('❌ signature_engineering_name está como "NOME"')
    else:
        print(f'✅ signature_engineering_name: {row[7]}')
    
    if row[8] == 'NOME':
        print('❌ signature_inspection2_name está como "NOME"')
    else:
        print(f'✅ signature_inspection2_name: {row[8]}')
    
    if row[3] == 'aaa':
        print('❌ equipment está como "aaa" (valor genérico)')
    else:
        print(f'✅ equipment: {row[3]}')
    
    # Verificar campos que aparecem com "TESTE:" na imagem
    if row[4] and 'TESTE:' in str(row[4]):
        print('⚠️  instruction_retrabalho contém "TESTE:" (dados de exemplo)')
    
    if row[5] and 'TESTE:' in str(row[5]):
        print('⚠️  cause_rnc contém "TESTE:" (dados de exemplo)')
    
    if row[6] and 'TESTE:' in str(row[6]):
        print('⚠️  action_rnc contém "TESTE:" (dados de exemplo)')
    
else:
    print('RNC não encontrada')

conn.close()
