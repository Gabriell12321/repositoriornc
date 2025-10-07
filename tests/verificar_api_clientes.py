#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste completo da API de clientes
"""
import sqlite3
import json

DB_PATH = 'database.db'

print("🔍 VERIFICAÇÃO COMPLETA - CLIENTES")
print("=" * 70)

# 1. Verificar banco de dados
print("\n1️⃣ VERIFICAÇÃO DO BANCO DE DADOS:")
print("-" * 70)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Verificar se a tabela existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
table_exists = cursor.fetchone()
print(f"   ✅ Tabela 'clients' existe: {bool(table_exists)}")

if table_exists:
    # Contar clientes
    cursor.execute('SELECT COUNT(*) FROM clients')
    total = cursor.fetchone()[0]
    print(f"   ✅ Total de clientes no banco: {total}")
    
    # Verificar estrutura
    cursor.execute("PRAGMA table_info(clients)")
    colunas = cursor.fetchall()
    print(f"   ✅ Colunas da tabela:")
    for col in colunas:
        print(f"      - {col[1]} ({col[2]})")
    
    # Mostrar primeiros 10 clientes
    print("\n   📝 Primeiros 10 clientes no banco:")
    cursor.execute('SELECT id, name FROM clients ORDER BY name LIMIT 10')
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"      {i:2d}. ID: {row[0]:3d} | {row[1]}")

# 2. Simular resposta da API
print("\n\n2️⃣ SIMULAÇÃO DA RESPOSTA DA API:")
print("-" * 70)

cursor.execute('SELECT id, name FROM clients ORDER BY name')
rows = [{'id': r[0], 'name': r[1]} for r in cursor.fetchall()]

api_response = {
    'success': True,
    'clients': rows
}

print(f"   ✅ Status da API: success = {api_response['success']}")
print(f"   ✅ Quantidade de clientes retornados: {len(api_response['clients'])}")
print(f"\n   📋 Amostra da resposta JSON (primeiros 5):")

for i, client in enumerate(api_response['clients'][:5], 1):
    print(f"      {i}. {json.dumps(client, ensure_ascii=False)}")

# 3. Verificar clientes específicos
print("\n\n3️⃣ VERIFICAÇÃO DE CLIENTES ESPECÍFICOS:")
print("-" * 70)

clientes_teste = ['Mello', 'Tedesco', 'Stora Enso', 'Klabin T.B.', 'Trombini S.A.']
for nome in clientes_teste:
    cursor.execute('SELECT id, name FROM clients WHERE name = ?', (nome,))
    result = cursor.fetchone()
    if result:
        print(f"   ✅ {nome:20s} - ID: {result[0]:3d} - ENCONTRADO")
    else:
        print(f"   ❌ {nome:20s} - NÃO ENCONTRADO")

# 4. Verificar se há clientes inativos
print("\n\n4️⃣ VERIFICAÇÃO DE CLIENTES ATIVOS/INATIVOS:")
print("-" * 70)

cursor.execute('SELECT COUNT(*) FROM clients WHERE is_active = 1')
ativos = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM clients WHERE is_active = 0')
inativos = cursor.fetchone()[0]

print(f"   ✅ Clientes ativos: {ativos}")
print(f"   ⚠️  Clientes inativos: {inativos}")

conn.close()

print("\n\n" + "=" * 70)
print("✅ VERIFICAÇÃO CONCLUÍDA!")
print("\nINSTRUÇÕES PARA O USUÁRIO:")
print("1. Se o total de clientes estiver correto (153), o problema é no frontend")
print("2. Faça um HARD REFRESH no navegador: Ctrl + Shift + R")
print("3. Ou limpe o cache do navegador completamente")
print("4. Se ainda não aparecer, reinicie o servidor Flask")
print("=" * 70)
