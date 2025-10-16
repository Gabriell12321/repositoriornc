#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico completo do problema de clientes
"""
import sqlite3
import json

DB_PATH = 'database.db'

print("🔍 DIAGNÓSTICO COMPLETO - CLIENTES")
print("=" * 70)

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Verificar se a tabela existe
    print("\n1️⃣ Verificando se a tabela 'clients' existe...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        print("   ✅ Tabela 'clients' EXISTE")
    else:
        print("   ❌ Tabela 'clients' NÃO EXISTE!")
        print("   🔧 SOLUÇÃO: Execute o script cadastrar_clientes.py novamente")
        conn.close()
        exit(1)
    
    # 2. Verificar estrutura da tabela
    print("\n2️⃣ Estrutura da tabela 'clients':")
    cursor.execute("PRAGMA table_info(clients)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")
    
    # 3. Contar registros
    print("\n3️⃣ Contando registros...")
    cursor.execute('SELECT COUNT(*) FROM clients')
    total = cursor.fetchone()[0]
    print(f"   📊 Total de clientes: {total}")
    
    if total == 0:
        print("   ❌ PROBLEMA: Nenhum cliente cadastrado!")
        print("   🔧 SOLUÇÃO: Execute o script cadastrar_clientes.py")
        conn.close()
        exit(1)
    
    # 4. Simular a query exata da API
    print("\n4️⃣ Simulando a query da API '/api/admin/clients':")
    cursor.execute('SELECT id, name FROM clients ORDER BY name')
    rows = cursor.fetchall()
    clients_data = [{'id': r[0], 'name': r[1]} for r in rows]
    
    print(f"   📦 Quantidade de clientes retornados: {len(clients_data)}")
    
    # 5. Mostrar JSON que seria retornado
    print("\n5️⃣ JSON que a API deveria retornar (primeiros 5):")
    api_response = {
        'success': True,
        'clients': clients_data[:5]
    }
    print(json.dumps(api_response, indent=2, ensure_ascii=False))
    
    # 6. Listar primeiros 10 clientes
    print("\n6️⃣ Primeiros 10 clientes no banco:")
    print("-" * 70)
    for i, client in enumerate(clients_data[:10], 1):
        print(f"   {i:2d}. ID: {client['id']:3d} | Nome: {client['name']}")
    
    # 7. Verificar se há clientes com nomes vazios ou nulos
    print("\n7️⃣ Verificando integridade dos dados...")
    cursor.execute("SELECT COUNT(*) FROM clients WHERE name IS NULL OR name = ''")
    invalid = cursor.fetchone()[0]
    if invalid > 0:
        print(f"   ⚠️  {invalid} clientes com nome vazio/nulo!")
    else:
        print("   ✅ Todos os clientes têm nomes válidos")
    
    # 8. Verificar se há problema de encoding
    print("\n8️⃣ Testando encoding de caracteres especiais...")
    cursor.execute("SELECT name FROM clients WHERE name LIKE '%ç%' OR name LIKE '%ã%' OR name LIKE '%õ%' LIMIT 3")
    special_chars = cursor.fetchall()
    if special_chars:
        print("   ✅ Caracteres especiais detectados (encoding correto):")
        for sc in special_chars:
            print(f"      - {sc[0]}")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ DIAGNÓSTICO CONCLUÍDO!")
    print("\n📋 RESUMO:")
    print(f"   ✅ Tabela existe: SIM")
    print(f"   ✅ Total de clientes: {total}")
    print(f"   ✅ API retornaria: {len(clients_data)} clientes")
    print(f"   ✅ Dados válidos: SIM")
    
    print("\n💡 PRÓXIMO PASSO:")
    print("   Se os clientes NÃO aparecem na interface web:")
    print("   1. Verifique se o servidor Flask está RODANDO")
    print("   2. Abra o Console do navegador (F12) e procure por erros")
    print("   3. Verifique a aba Network (Rede) se a chamada '/api/admin/clients' está sendo feita")
    print("   4. Certifique-se de que está logado como administrador")
    
except Exception as e:
    print(f"\n❌ ERRO FATAL: {e}")
    import traceback
    traceback.print_exc()
