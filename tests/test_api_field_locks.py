#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import time

def test_field_locks_api():
    """Testa a API de field_locks"""
    base_url = "http://localhost:5001/admin/field-locks/api"
    
    print("🧪 Testando API Field Locks...")
    
    # Aguardar servidor inicializar
    time.sleep(2)
    
    try:
        # Teste 1: Buscar grupos
        print("\n1️⃣ Testando GET /groups")
        response = requests.get(f"{base_url}/groups", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso! {len(data)} grupos encontrados")
            for group in data:
                print(f"   - Grupo {group['id']}: {group['name']}")
        else:
            print(f"❌ Erro: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor na porta 5001")
        print("   Verifique se o servidor field_locks está rodando")
        
    except requests.exceptions.Timeout:
        print("❌ Erro: Timeout na conexão")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_field_locks_api()