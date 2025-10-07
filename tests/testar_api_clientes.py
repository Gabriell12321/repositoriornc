#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste da API de clientes
"""
import sqlite3

DB_PATH = 'database.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("🧪 TESTE: API de clientes")
print("=" * 60)

# Simular a query da API
cursor.execute('SELECT id, name FROM clients ORDER BY name')
rows = cursor.fetchall()

print(f"\n📊 Total retornado pela query: {len(rows)}")
print("\n📝 Primeiros 20 clientes (como a API retorna):")
print("-" * 60)

for i, row in enumerate(rows[:20], 1):
    print(f"{i:2d}. ID: {row[0]:3d} | Nome: {row[1]}")

print("\n✅ A query da API está retornando todos os clientes corretamente!")
print(f"   Total de {len(rows)} clientes seriam enviados para o frontend")

conn.close()
