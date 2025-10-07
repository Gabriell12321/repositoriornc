#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste simples de salvamento de permissões
Simula o que o frontend faz quando salva uma alteração
"""

import requests
import json

def test_save_permissions():
    """Testa o salvamento de permissões"""
    base_url = "http://localhost:5001/admin/field-locks/api"
    
    # Dados de teste - simula o que vem do frontend
    test_data = {
        "locks": {
            "title": True,
            "description": False,
            "priority": True,
            "price": False,
            "responsavel": True
        }
    }
    
    try:
        print("🧪 Testando salvamento de permissões...")
        print(f"📤 Enviando dados: {json.dumps(test_data, indent=2)}")
        
        # Testar com grupo ID 1 (teste)
        response = requests.post(
            f"{base_url}/locks/1",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        try:
            result = response.json()
            print(f"✅ Resposta JSON: {json.dumps(result, indent=2)}")
        except:
            print(f"❌ Resposta não é JSON: {response.text}")
            
        if response.status_code == 200:
            print("🎉 Salvamento funcionou!")
        else:
            print(f"⚠️  Erro no salvamento: Status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está rodando na porta 5001")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_save_permissions()