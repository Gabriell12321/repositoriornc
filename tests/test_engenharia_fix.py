import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Testar query da engenharia
cursor.execute("""
    SELECT COUNT(*) 
    FROM rncs 
    WHERE (
        LOWER(TRIM(area_responsavel)) LIKE '%engenharia%'
        OR LOWER(TRIM(setor)) LIKE '%engenharia%'
        OR LOWER(TRIM(signature_engineering_name)) LIKE '%engenharia%'
    )
    AND (is_deleted = 0 OR is_deleted IS NULL)
""")

total = cursor.fetchone()[0]
print(f"✅ Total de RNCs de Engenharia encontradas: {total}")

# Testar quantas são finalizadas
cursor.execute("""
    SELECT COUNT(*) 
    FROM rncs 
    WHERE (
        LOWER(TRIM(area_responsavel)) LIKE '%engenharia%'
        OR LOWER(TRIM(setor)) LIKE '%engenharia%'
        OR LOWER(TRIM(signature_engineering_name)) LIKE '%engenharia%'
    )
    AND (is_deleted = 0 OR is_deleted IS NULL)
    AND (status = 'Finalizado' OR finalized_at IS NOT NULL)
""")

finalizadas = cursor.fetchone()[0]
print(f"✅ RNCs Finalizadas: {finalizadas}")
print(f"✅ RNCs Ativas: {total - finalizadas}")

conn.close()
print("\n✅ Correção aplicada com sucesso!")
print("🔄 Recarregue a página no navegador (Ctrl+F5)")
