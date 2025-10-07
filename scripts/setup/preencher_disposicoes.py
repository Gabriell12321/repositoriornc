import sqlite3

print("🔄 Preenchendo disposições para todas as RNCs...")

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Buscar todas as RNCs que NÃO têm disposição marcada
cursor.execute("""
    SELECT id, rnc_number, instruction_retrabalho, description
    FROM rncs 
    WHERE disposition_usar = 0 
    AND disposition_retrabalhar = 0 
    AND disposition_rejeitar = 0 
    AND disposition_sucata = 0 
    AND disposition_devolver_estoque = 0 
    AND disposition_devolver_fornecedor = 0
""")

rncs_sem_disposicao = cursor.fetchall()
total = len(rncs_sem_disposicao)

print(f"📊 Encontradas {total} RNCs sem disposição marcada")
print(f"")

contador = 0
for rnc in rncs_sem_disposicao:
    rnc_id, rnc_number, instrucao, descricao = rnc
    
    # Analisar texto para definir disposição
    texto_completo = (instrucao or "") + " " + (descricao or "")
    texto_lower = texto_completo.lower()
    
    # Definir disposição baseado em palavras-chave
    usar = 0
    retrabalhar = 0
    rejeitar = 0
    sucata = 0
    devolver_estoque = 0
    devolver_fornecedor = 0
    
    if any(palavra in texto_lower for palavra in ['retrabalhar', 'reusinar', 'corrigir', 'refazer', 'ajustar', 'usinar']):
        retrabalhar = 1
    elif any(palavra in texto_lower for palavra in ['sucata', 'refugar']):
        sucata = 1
    elif any(palavra in texto_lower for palavra in ['rejeitar', 'devolver fornecedor', 'terceiro']):
        devolver_fornecedor = 1
    elif any(palavra in texto_lower for palavra in ['nova', 'novo', 'novas peças']):
        retrabalhar = 1
    elif any(palavra in texto_lower for palavra in ['como está', 'aceitar', 'usar']):
        usar = 1
    else:
        # Se não identificou, marca retrabalhar como padrão
        retrabalhar = 1
    
    # Atualizar RNC
    cursor.execute("""
        UPDATE rncs 
        SET disposition_usar = ?,
            disposition_retrabalhar = ?,
            disposition_rejeitar = ?,
            disposition_sucata = ?,
            disposition_devolver_estoque = ?,
            disposition_devolver_fornecedor = ?
        WHERE id = ?
    """, (usar, retrabalhar, rejeitar, sucata, devolver_estoque, devolver_fornecedor, rnc_id))
    
    contador += 1
    if contador % 100 == 0:
        print(f"✅ Processadas {contador}/{total} RNCs...")

conn.commit()

print(f"")
print(f"✅ CONCLUÍDO! {contador} RNCs atualizadas com disposição")
print(f"")

# Verificar resultado
cursor.execute("""
    SELECT COUNT(*) 
    FROM rncs 
    WHERE disposition_usar = 1 
    OR disposition_retrabalhar = 1 
    OR disposition_rejeitar = 1 
    OR disposition_sucata = 1 
    OR disposition_devolver_estoque = 1 
    OR disposition_devolver_fornecedor = 1
""")
com_disposicao = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM rncs")
total_rncs = cursor.fetchone()[0]

print(f"📊 RESULTADO FINAL:")
print(f"   Total de RNCs: {total_rncs}")
print(f"   RNCs com disposição: {com_disposicao} ({com_disposicao*100/total_rncs:.1f}%)")

# Estatísticas por tipo
cursor.execute("SELECT COUNT(*) FROM rncs WHERE disposition_usar = 1")
usar_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM rncs WHERE disposition_retrabalhar = 1")
retrabalhar_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM rncs WHERE disposition_sucata = 1")
sucata_count = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM rncs WHERE disposition_devolver_fornecedor = 1")
devolver_count = cursor.fetchone()[0]

print(f"")
print(f"📈 DISTRIBUIÇÃO:")
print(f"   Usar como está: {usar_count}")
print(f"   Retrabalhar: {retrabalhar_count}")
print(f"   Sucata: {sucata_count}")
print(f"   Devolver ao fornecedor: {devolver_count}")

conn.close()

print(f"")
print(f"🎉 Processo concluído com sucesso!")
