#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste das APIs de usuários e grupos
"""

import requests
import json

def test_user_group_apis():
    base_url = "http://localhost:5000"
    
    print("🧪 Testando APIs de usuários e grupos...")
    
    # Teste da API de grupos
    print("\n📊 Testando /api/groups")
    try:
        response = requests.get(f"{base_url}/api/groups", timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Grupos encontrados: {len(data)} grupos")
            for group in data:
                print(f"     - {group.get('name', 'Nome não disponível')} (ID: {group.get('id', 'N/A')})")
        else:
            print(f"   ❌ Erro: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Erro: Não foi possível conectar ao servidor")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Teste da API de usuários
    print("\n👥 Testando /api/users")
    try:
        response = requests.get(f"{base_url}/api/users", timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Usuários encontrados: {len(data)} usuários")
            for user in data:
                print(f"     - {user.get('username', 'N/A')} - Grupo: {user.get('group_name', 'N/A')}")
        else:
            print(f"   ❌ Erro: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Erro: Não foi possível conectar ao servidor")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

if __name__ == "__main__":
    test_user_group_apis()