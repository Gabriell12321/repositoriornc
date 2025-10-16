#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

print("=== TESTE DA API DE FIELD LOCKS ===")

base_url = "http://127.0.0.1:5000"

def test_field_locks_api():
    try:
        # Testar API de grupos
        print("\n🔍 Testando API de grupos...")
        response = requests.get(f"{base_url}/admin/field-locks/api/groups", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            groups = response.json()
            print(f"   ✅ Groups (parsed): {groups}")
            print(f"   📊 Groups type: {type(groups)}")
            
            if groups and len(groups) > 0:
                # Testar locks para o primeiro grupo
                first_group = groups[0]
                group_id = first_group['id']
                print(f"\n🔍 Testing locks for group {group_id}")
                
                locks_response = requests.get(f"{base_url}/admin/field-locks/api/locks/{group_id}", timeout=10)
                print(f"   Status: {locks_response.status_code}")
                print(f"   Response: {locks_response.text}")
                
                if locks_response.status_code == 200:
                    locks = locks_response.json()
                    print(f"   ✅ Locks (parsed): {locks}")
                    print(f"   📊 Locks type: {type(locks)}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    test_field_locks_api()