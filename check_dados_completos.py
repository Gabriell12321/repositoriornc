#!/usr/bin/env python3
"""Verificar dados completos de uma RNC de exemplo."""

import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Pegar uma RNC com dados completos
cursor.execute("""
    SELECT id, rnc_number, responsavel, setor, inspetor, material, quantity, drawing,
           equipment, client, price, instruction_retrabalho, cause_rnc, action_rnc,
           description, title
    FROM rncs 
    WHERE responsavel IS NOT NULL 
      AND responsavel != '' 
    LIMIT 3
""")

results = cursor.fetchall()

print("📋 EXEMPLO DE DADOS COMPLETOS DAS RNCS:")
print("=" * 60)

for i, rnc in enumerate(results):
    print(f"\n🔸 RNC {i+1}: {rnc[1]}")
    print(f"   Responsável: {rnc[2]}")
    print(f"   Setor: {rnc[3]}")
    print(f"   Inspetor: {rnc[4]}")
    print(f"   Material: {rnc[5]}")
    print(f"   Quantidade: {rnc[6]}")
    print(f"   Desenho: {rnc[7]}")
    print(f"   Equipamento: {rnc[8]}")
    print(f"   Cliente: {rnc[9]}")
    print(f"   Preço: {rnc[10]}")
    print(f"   Instrução Retrabalho: {rnc[11]}")
    print(f"   Causa RNC: {rnc[12]}")
    print(f"   Ação RNC: {rnc[13]}")

conn.close()