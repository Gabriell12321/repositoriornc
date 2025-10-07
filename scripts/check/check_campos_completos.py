#!/usr/bin/env python3
"""Verificar se existem dados separados para setor e área responsável."""

import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Verificar todos os campos disponíveis relacionados
cursor.execute("PRAGMA table_info(rncs)")
all_cols = [col[1] for col in cursor.fetchall()]

print("📋 TODOS OS CAMPOS DA TABELA RNCS:")
print("=" * 50)
for i, col in enumerate(all_cols, 1):
    print(f"{i:2d}. {col}")

print("\n🔍 CAMPOS RELACIONADOS A SETOR/ÁREA:")
print("=" * 40)
related_fields = [col for col in all_cols if any(term in col.lower() for term in ['setor', 'area', 'responsavel', 'department'])]
for field in related_fields:
    print(f"  ✓ {field}")

# Verificar alguns dados de exemplo
print("\n📊 DADOS DE EXEMPLO:")
print("=" * 30)

cursor.execute("""
    SELECT rnc_number, responsavel, setor, user_id, assigned_user_id
    FROM rncs 
    WHERE responsavel IS NOT NULL AND responsavel != ''
    LIMIT 5
""")

results = cursor.fetchall()
for rnc in results:
    print(f"RNC {rnc[0]}:")
    print(f"  📋 Responsável: {rnc[1]}")
    print(f"  🏢 Setor: {rnc[2] or 'N/A'}")
    print(f"  👤 User ID: {rnc[3] or 'N/A'}")
    print(f"  👥 Assigned User ID: {rnc[4] or 'N/A'}")
    print()

conn.close()