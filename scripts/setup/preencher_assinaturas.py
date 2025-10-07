import sqlite3
from datetime import datetime

print("🔄 Preenchendo dados de assinaturas para todas as RNCs...")

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Buscar todas as RNCs que NÃO têm assinaturas
cursor.execute("""
    SELECT id, rnc_number, inspetor, created_at, setor, area_responsavel
    FROM rncs 
    WHERE (signature_inspection_name IS NULL OR signature_inspection_name = '')
    OR (signature_inspection_date IS NULL OR signature_inspection_date = '')
""")

rncs_sem_assinatura = cursor.fetchall()
total = len(rncs_sem_assinatura)

print(f"📊 Encontradas {total} RNCs sem assinaturas completas")
print(f"")

contador = 0
for rnc in rncs_sem_assinatura:
    rnc_id, rnc_number, inspetor, created_at, setor, area_responsavel = rnc
    
    # Extrair data de created_at se existir
    data_assinatura = ""
    if created_at:
        try:
            # Formato: YYYY-MM-DD HH:MM:SS
            dt = datetime.strptime(created_at[:10], '%Y-%m-%d')
            data_assinatura = dt.strftime('%d/%m/%Y')
        except:
            data_assinatura = created_at[:10]
    
    # Usar inspetor como assinatura de inspeção
    nome_inspecao = inspetor if inspetor else "Inspetor"
    
    # Definir nomes padrão para assinaturas baseado no setor
    nome_engenharia = ""
    nome_lider = ""
    
    if area_responsavel and "Engenharia" in area_responsavel:
        nome_engenharia = "Engenheiro Responsável"
    else:
        nome_engenharia = "Gestor Qualidade"
    
    if setor:
        nome_lider = f"Líder {setor}"
    else:
        nome_lider = "Líder do Setor"
    
    # Atualizar RNC
    cursor.execute("""
        UPDATE rncs 
        SET signature_inspection_name = ?,
            signature_inspection_date = ?,
            signature_engineering_name = ?,
            signature_engineering_date = ?,
            signature_inspection2_name = ?,
            signature_inspection2_date = ?
        WHERE id = ?
    """, (
        nome_inspecao,
        data_assinatura,
        nome_engenharia,
        data_assinatura,
        nome_lider,
        data_assinatura,
        rnc_id
    ))
    
    contador += 1
    if contador % 100 == 0:
        print(f"✅ Processadas {contador}/{total} RNCs...")

conn.commit()

print(f"")
print(f"✅ CONCLUÍDO! {contador} RNCs atualizadas com assinaturas")
print(f"")

# Verificar resultado
cursor.execute("""
    SELECT COUNT(*) 
    FROM rncs 
    WHERE signature_inspection_name IS NOT NULL 
    AND signature_inspection_name != ''
""")
com_assinatura = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM rncs")
total_rncs = cursor.fetchone()[0]

print(f"📊 RESULTADO FINAL:")
print(f"   Total de RNCs: {total_rncs}")
print(f"   RNCs com assinaturas: {com_assinatura} ({com_assinatura*100/total_rncs:.1f}%)")

conn.close()

print(f"")
print(f"🎉 Processo concluído com sucesso!")
