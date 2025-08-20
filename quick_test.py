#!/usr/bin/env python3
import sqlite3

# Teste direto no banco de dados
conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

print("=== TESTE DIRETO NO BANCO ===")

# 1. Verificar estrutura
cursor.execute("PRAGMA table_info(rncs)")
columns = [col[1] for col in cursor.fetchall()]
print(f"Colunas da tabela rncs: {columns}")

# 2. Verificar se department existe
if 'department' in columns:
    print("✅ Coluna department existe!")
    
    # 3. Contar RNCs com departamento
    cursor.execute("SELECT COUNT(*) FROM rncs WHERE department IS NOT NULL AND department != ''")
    count = cursor.fetchone()[0]
    print(f"RNCs com departamento: {count}")
    
    # 4. Verificar exemplos
    cursor.execute("SELECT id, rnc_number, department, user_id FROM rncs WHERE department = 'Engenharia' ORDER BY id DESC LIMIT 3")
    eng_rncs = cursor.fetchall()
    print("RNCs do departamento Engenharia:")
    for rnc_id, rnc_num, dept, user_id in eng_rncs:
        print(f"  - {rnc_num}: {dept} (User: {user_id})")
else:
    print("❌ Coluna department não existe!")

conn.close()
print("Teste concluído.")
