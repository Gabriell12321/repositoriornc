#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simulando exatamente o que o servidor Flask faz
"""
import sqlite3
import json

DB_PATH = 'database.db'

print("🧪 SIMULAÇÃO DA API DO SERVIDOR FLASK")
print("=" * 70)

# Simular ensure_clients_table()
print("\n1️⃣ Executando ensure_clients_table()...")
try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()
    print("   ✅ Tabela clients verificada/criada")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# Simular api_list_clients()
print("\n2️⃣ Simulando GET /api/admin/clients...")
try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT id, name FROM clients ORDER BY name')
    rows = [{'id': r[0], 'name': r[1]} for r in cur.fetchall()]
    conn.close()
    
    # Criar resposta JSON
    response = {'success': True, 'clients': rows}
    
    print(f"   ✅ Query executada com sucesso")
    print(f"   📦 Total de clientes retornados: {len(rows)}")
    print(f"\n   📄 Resposta JSON (primeiros 3):")
    sample_response = {'success': True, 'clients': rows[:3]}
    print(json.dumps(sample_response, indent=2, ensure_ascii=False))
    
    if len(rows) == 0:
        print("\n   ❌ PROBLEMA: A query retornou 0 clientes!")
    else:
        print(f"\n   ✅ SUCESSO: {len(rows)} clientes seriam enviados ao frontend")
        
except Exception as e:
    print(f"   ❌ Erro na query: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("💡 CONCLUSÃO:")
print("   Se este teste retornou 153 clientes mas a interface mostra 0:")
print("   ➡️  O servidor Flask precisa ser REINICIADO!")
print("   ➡️  Abra o console do navegador (F12) para ver erros JavaScript")
print("   ➡️  Verifique a aba Network se a chamada à API está retornando 200 OK")
