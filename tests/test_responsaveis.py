#!/usr/bin/env python3
"""Teste para verificar se os responsáveis estão sendo retornados corretamente."""

import sqlite3

# Simular a query da API
conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

sql = """
    SELECT 
        r.id, r.rnc_number, r.title, r.equipment, r.client, r.priority, r.status, 
        r.user_id, r.assigned_user_id, r.created_at, r.updated_at, r.finalized_at, 
        r.responsavel, u.department AS user_department, au.name AS assigned_user_name
    FROM rncs r
    LEFT JOIN users u ON r.user_id = u.id
    LEFT JOIN users au ON r.assigned_user_id = au.id
    WHERE (r.is_deleted = 0 OR r.is_deleted IS NULL) 
      AND r.status NOT IN ('Finalizado')
    ORDER BY r.id DESC
    LIMIT 5
"""

cursor.execute(sql)
results = cursor.fetchall()

print("🔍 TESTE DA QUERY DA API:")
print("=" * 50)

for i, rnc in enumerate(results):
    print(f"\n📝 RNC {i+1}:")
    print(f"   ID: {rnc[0]}")
    print(f"   Número: {rnc[1]}")
    print(f"   Título: {rnc[2]}")
    print(f"   Responsável (índice 12): {rnc[12]}")
    print(f"   User Department (índice 13): {rnc[13]}")
    
    # Simular o mapeamento da API
    formatted = {
        'id': rnc[0],
        'rnc_number': rnc[1],
        'title': rnc[2],
        'user_name': rnc[12],  # Este deveria ser o responsavel
    }
    print(f"   ✅ Formatado user_name: {formatted['user_name']}")

conn.close()