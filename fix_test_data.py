import sqlite3

print("=== LIMPEZA DE DADOS DE TESTE ===")

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# RNC específica para corrigir
rnc_number = 'RNC-2025-08-28-104553'

# Verificar dados atuais
cursor.execute('''
    SELECT id, rnc_number, title, equipment, instruction_retrabalho, cause_rnc, action_rnc, 
           signature_engineering_name, signature_inspection2_name
    FROM rncs 
    WHERE rnc_number = ?
''', (rnc_number,))
row = cursor.fetchone()

if row:
    print(f"✅ RNC encontrada: {row[1]}")
    print(f"ID: {row[0]}")
    
    # Dados para atualização
    update_data = {
        'equipment': 'Equipamento de Usinagem CNC',
        'signature_engineering_name': 'João Silva - Gerente de Engenharia',
        'signature_inspection2_name': 'Maria Santos - Líder de Qualidade',
        'instruction_retrabalho': 'Verificar dimensões da peça e refazer usinagem conforme desenho técnico',
        'cause_rnc': 'Erro na fixação da peça durante usinagem causou desvio dimensional',
        'action_rnc': 'Recalibrar dispositivos de fixação e retreinar operador responsável'
    }
    
    print("\n=== ATUALIZANDO DADOS ===")
    
    # Atualizar cada campo
    for field, new_value in update_data.items():
        cursor.execute(f'UPDATE rncs SET {field} = ? WHERE rnc_number = ?', (new_value, rnc_number))
        print(f"✅ {field}: '{new_value}'")
    
    # Commit das alterações
    conn.commit()
    print("\n✅ Dados atualizados com sucesso!")
    
    # Verificar dados após atualização
    cursor.execute('''
        SELECT id, rnc_number, title, equipment, instruction_retrabalho, cause_rnc, action_rnc, 
               signature_engineering_name, signature_inspection2_name
        FROM rncs 
        WHERE rnc_number = ?
    ''', (rnc_number,))
    updated_row = cursor.fetchone()
    
    print("\n=== DADOS APÓS ATUALIZAÇÃO ===")
    print(f"Equipment: {updated_row[3]}")
    print(f"Signature Engineering: {updated_row[7]}")
    print(f"Signature Inspection2: {updated_row[8]}")
    print(f"Instruction: {updated_row[4]}")
    print(f"Cause: {updated_row[5]}")
    print(f"Action: {updated_row[6]}")
    
else:
    print(f"❌ RNC {rnc_number} não encontrada")

conn.close()
print("\n=== LIMPEZA CONCLUÍDA ===")
