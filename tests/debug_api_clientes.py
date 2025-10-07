#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste completo da API de clientes - simula requisição real
"""
import sqlite3
import json

DB_PATH = 'database.db'

def test_api_endpoint():
    """Simula exatamente o que a API /api/admin/clients faz"""
    print("🧪 TESTE COMPLETO DA API /api/admin/clients")
    print("=" * 70)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Query exata da API
        cursor.execute('SELECT id, name FROM clients ORDER BY name')
        rows = cursor.fetchall()
        
        # Formatar como a API faz
        clients_list = [{'id': r[0], 'name': r[1]} for r in rows]
        
        # Criar resposta JSON como a API
        response = {
            'success': True,
            'clients': clients_list
        }
        
        print(f"\n✅ Conexão com banco: OK")
        print(f"✅ Query executada: OK")
        print(f"✅ Total de registros: {len(clients_list)}")
        print(f"\n📦 Resposta JSON (primeiros 5 clientes):")
        print("-" * 70)
        
        # Mostrar JSON como seria enviado
        sample_response = {
            'success': True,
            'clients': clients_list[:5]
        }
        print(json.dumps(sample_response, indent=2, ensure_ascii=False))
        
        print("\n📝 Lista completa dos primeiros 20 clientes:")
        print("-" * 70)
        for i, client in enumerate(clients_list[:20], 1):
            print(f"{i:2d}. ID: {client['id']:3d} | Nome: {client['name']}")
        
        conn.close()
        
        print("\n" + "=" * 70)
        print(f"✅ API retornaria {len(clients_list)} clientes corretamente!")
        
        # Verificar se tabela existe e tem estrutura correta
        print("\n🔍 Verificando estrutura da tabela:")
        print("-" * 70)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(clients)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   Coluna: {col[1]:15s} | Tipo: {col[2]:10s} | NOT NULL: {col[3]}")
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_api_endpoint()
