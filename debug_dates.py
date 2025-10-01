#!/usr/bin/env python3
"""Debug da formatação de datas no sistema."""

import sqlite3
import json
from datetime import datetime

# Conectar ao banco
conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Buscar algumas RNCs
cursor.execute("""
    SELECT id, rnc_number, created_at, finalized_at 
    FROM rncs 
    ORDER BY id 
    LIMIT 5
""")

rncs = cursor.fetchall()

print("🔍 DEBUG DAS DATAS NO BANCO:")
print("=" * 50)

for rnc in rncs:
    rnc_id, rnc_number, created_at, finalized_at = rnc
    print(f"\n📝 RNC {rnc_number} (ID: {rnc_id})")
    print(f"   📅 created_at (raw): {created_at}")
    print(f"   📅 created_at (type): {type(created_at)}")
    print(f"   📅 finalized_at (raw): {finalized_at}")
    
    # Tentar diferentes formatações
    if created_at:
        # Como string ISO
        print(f"   🔄 ISO string: {created_at}")
        
        # Tentar parsear como datetime
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            print(f"   ✅ Parsed datetime: {dt}")
            print(f"   📋 Formatted (pt-BR): {dt.strftime('%d/%m/%Y')}")
        except Exception as e:
            print(f"   ❌ Erro ao parsear: {e}")

conn.close()

print("\n" + "=" * 50)
print("🧪 SIMULAÇÃO DO JAVASCRIPT:")

# Simular o que o JavaScript faz
test_date = "2023-01-02"
print(f"Data do banco: {test_date}")

# Simular new Date(r.created_at).toLocaleDateString('pt-BR')
from datetime import datetime
try:
    js_date = datetime.fromisoformat(test_date)
    formatted = js_date.strftime('%d/%m/%Y')
    print(f"Formatação simulada: {formatted}")
except Exception as e:
    print(f"Erro na simulação: {e}")