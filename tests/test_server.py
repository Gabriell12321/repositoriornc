#!/usr/bin/env python3
"""
Script para testar se o servidor está funcionando
"""

import requests
import json

def test_server():
    """Testar se o servidor está funcionando"""
    
    # URL do servidor
    base_url = "http://192.168.2.114:5001"
    
    try:
        # Testar se o servidor está respondendo
        print("🔍 Testando conexão com o servidor...")
        response = requests.get(f"{base_url}/", timeout=5)
        
        if response.status_code == 200:
            print("✅ Servidor está respondendo!")
        else:
            print(f"⚠️ Servidor respondeu com status {response.status_code}")
            
        # Testar a rota de listar RNCs
        print("\n📋 Testando rota de listar RNCs...")
        list_response = requests.get(f"{base_url}/api/rnc/list?tab=active")
        
        print(f"📊 Status Code: {list_response.status_code}")
        print(f"📄 Response Headers: {dict(list_response.headers)}")
        
        if list_response.status_code == 200:
            data = list_response.json()
            print(f"✅ Rota funcionando! RNCs encontrados: {len(data.get('rncs', []))}")
        else:
            print(f"❌ Erro na rota: {list_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão: Servidor não está rodando ou não acessível")
        print("💡 Certifique-se de que o servidor está rodando com: python server_form.py")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_server() 