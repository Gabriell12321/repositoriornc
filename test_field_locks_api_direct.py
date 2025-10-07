#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar a API de field_locks diretamente
"""

import requests
import json

BASE_URL = "http://localhost:5001"

def test_field_locks_api():
    """Testa a API de field_locks"""
    
    print("=" * 60)
    print("🧪 TESTANDO API DE FIELD LOCKS")
    print("=" * 60)
    
    # Teste 1: Listar grupos
    print("\n1️⃣ Teste: Listar grupos")
    print("-" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/admin/field-locks/api/groups", timeout=5)
        print(f"Status: {response.status_code}")
        
        if response.ok:
            groups = response.json()
            print(f"✅ {len(groups)} grupos encontrados")
            for group in groups:
                print(f"   - ID: {group['id']}, Nome: {group['name']}")
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 2: Buscar locks de um grupo (creation)
    print("\n2️⃣ Teste: Buscar locks do grupo 7 (Engenharia - creation)")
    print("-" * 60)
    
    group_id = 7
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/field-locks/api/locks/{group_id}",
            params={'context': 'creation'},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        
        if response.ok:
            data = response.json()
            locks = data.get('locks', {})
            print(f"✅ {len(locks)} campos configurados")
            
            locked = sum(1 for v in locks.values() if v)
            unlocked = len(locks) - locked
            print(f"   - Bloqueados: {locked}")
            print(f"   - Liberados: {unlocked}")
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    # Teste 3: Atualizar locks (response context)
    print("\n3️⃣ Teste: Atualizar locks do grupo 7 (Engenharia - response)")
    print("-" * 60)
    
    test_locks = {
        'title': True,
        'equipment': False,
        'client': True,
        'description': False,
        'price': True
    }
    
    payload = {
        'context': 'response',
        'locks': test_locks
    }
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/admin/field-locks/api/locks/{group_id}",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.ok:
            result = response.json()
            print(f"✅ Sucesso: {result.get('message')}")
            print(f"   - Atualizados: {result.get('updated_count')}")
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ TESTES CONCLUÍDOS")
    print("=" * 60)

if __name__ == '__main__':
    test_field_locks_api()
