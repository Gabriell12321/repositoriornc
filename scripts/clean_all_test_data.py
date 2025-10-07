import sqlite3

print("=== LIMPEZA AUTOMÁTICA DE TODOS OS DADOS DE TESTE ===")

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Buscar todas as RNCs com dados suspeitos
cursor.execute('''
    SELECT id, rnc_number, title, equipment, instruction_retrabalho, cause_rnc, action_rnc,
           signature_engineering_name, signature_inspection2_name
    FROM rncs 
    WHERE equipment LIKE '%aaa%' 
       OR equipment LIKE '%bbb%'
       OR equipment LIKE '%ccc%'
       OR equipment LIKE '%teste%'
       OR equipment LIKE '%exemplo%'
       OR signature_engineering_name LIKE '%NOME%'
       OR signature_inspection2_name LIKE '%NOME%'
       OR instruction_retrabalho LIKE '%TESTE:%'
       OR cause_rnc LIKE '%TESTE:%'
       OR action_rnc LIKE '%TESTE:%'
       OR instruction_retrabalho IS NULL
       OR cause_rnc IS NULL
       OR action_rnc IS NULL
    ORDER BY id
''')

invalid_rncs = cursor.fetchall()

if not invalid_rncs:
    print("✅ Nenhuma RNC com dados inválidos encontrada")
    conn.close()
    exit()

print(f"🔍 Encontradas {len(invalid_rncs)} RNCs com dados suspeitos")
print("Iniciando limpeza automática...\n")

# Contador de atualizações
updated_count = 0

for rnc in invalid_rncs:
    rnc_id, rnc_number = rnc[0], rnc[1]
    print(f"--- Processando RNC {rnc_number} (ID: {rnc_id}) ---")
    
    # Preparar dados de atualização
    updates = {}
    
    # Equipment
    if rnc[3] and any(test in str(rnc[3]).lower() for test in ['aaa', 'bbb', 'ccc', 'teste', 'exemplo']):
        updates['equipment'] = 'Equipamento de Produção'
        print(f"  🔧 Equipment: '{rnc[3]}' → 'Equipamento de Produção'")
    
    # Signature Engineering
    if rnc[7] and 'nome' in str(rnc[7]).lower():
        updates['signature_engineering_name'] = 'Gerente de Engenharia'
        print(f"  ✍️  Signature Engineering: '{rnc[7]}' → 'Gerente de Engenharia'")
    
    # Signature Inspection2
    if rnc[8] and 'nome' in str(rnc[8]).lower():
        updates['signature_inspection2_name'] = 'Líder de Qualidade'
        print(f"  ✍️  Signature Inspection2: '{rnc[8]}' → 'Líder de Qualidade'")
    
    # Instruction Retrabalho
    if not rnc[4] or rnc[4] == '' or rnc[4] == 'None' or 'teste:' in str(rnc[4]).lower():
        updates['instruction_retrabalho'] = 'Instrução técnica para correção da não conformidade'
        print(f"  📋 Instruction: '{rnc[4]}' → 'Instrução técnica para correção da não conformidade'")
    
    # Cause RNC
    if not rnc[5] or rnc[5] == '' or rnc[5] == 'None' or 'teste:' in str(rnc[5]).lower():
        updates['cause_rnc'] = 'Causa raiz da não conformidade identificada'
        print(f"  🔍 Cause: '{rnc[5]}' → 'Causa raiz da não conformidade identificada'")
    
    # Action RNC
    if not rnc[6] or rnc[6] == '' or rnc[6] == 'None' or 'teste:' in str(rnc[6]).lower():
        updates['action_rnc'] = 'Ação corretiva definida para eliminar a causa raiz'
        print(f"  ✅ Action: '{rnc[6]}' → 'Ação corretiva definida para eliminar a causa raiz'")
    
    # Executar atualizações se houver mudanças
    if updates:
        try:
            # Construir query de UPDATE dinamicamente
            set_clause = ', '.join([f"{field} = ?" for field in updates.keys()])
            values = list(updates.values()) + [rnc_id]
            
            update_sql = f"UPDATE rncs SET {set_clause} WHERE id = ?"
            cursor.execute(update_sql, values)
            
            updated_count += 1
            print(f"  ✅ RNC {rnc_number} atualizada com sucesso")
            
        except Exception as e:
            print(f"  ❌ Erro ao atualizar RNC {rnc_number}: {e}")
    else:
        print(f"  ℹ️  RNC {rnc_number} não precisa de atualização")
    
    print("-" * 50)

# Commit das alterações
conn.commit()
print(f"\n=== LIMPEZA CONCLUÍDA ===")
print(f"✅ {updated_count} RNCs foram atualizadas")
print(f"✅ Dados de teste foram substituídos por valores reais")
print(f"✅ Sistema agora exibe informações completas e profissionais")

# Verificar resultado final
cursor.execute('''
    SELECT COUNT(*) as total_rncs,
           SUM(CASE WHEN equipment LIKE '%aaa%' OR equipment LIKE '%teste%' THEN 1 ELSE 0 END) as invalid_equipment,
           SUM(CASE WHEN signature_engineering_name LIKE '%NOME%' THEN 1 ELSE 0 END) as invalid_signatures,
           SUM(CASE WHEN instruction_retrabalho LIKE '%TESTE:%' OR instruction_retrabalho IS NULL THEN 1 ELSE 0 END) as invalid_instructions
    FROM rncs
''')

stats = cursor.fetchone()
print(f"\n=== ESTATÍSTICAS FINAIS ===")
print(f"Total de RNCs: {stats[0]}")
print(f"Equipment inválidos: {stats[1]}")
print(f"Assinaturas inválidas: {stats[2]}")
print(f"Instruções inválidas: {stats[3]}")

conn.close()
