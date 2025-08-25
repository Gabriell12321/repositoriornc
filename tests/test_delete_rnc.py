#!/usr/bin/env python3
"""
Script para testar a rota de deletar RNC
"""

import requests
import json

def test_delete_rnc():
    """Testar a rota de deletar RNC"""
    
    # URL do servidor (ajuste conforme necessário)
    base_url = "http://192.168.2.114:5001"
    
    # Primeiro, fazer login para obter sessão
    login_data = {
        "email": "admin@ippel.com.br",
        "password": "admin123"
    }
    
    try:
        # Fazer login
        print("🔐 Fazendo login...")
        login_response = requests.post(f"{base_url}/api/login", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Erro no login: {login_response.status_code}")
            print(login_response.text)
            return
        
        print("✅ Login realizado com sucesso!")
        
        # Obter cookies da sessão
        cookies = login_response.cookies
        
        # Testar a rota de deletar RNC
        rnc_id = 2  # ID da RNC que você está tentando deletar
        print(f"🗑️ Testando deletar RNC {rnc_id}...")
        
        delete_response = requests.delete(
            f"{base_url}/api/rnc/{rnc_id}/delete",
            cookies=cookies
        )
        
        print(f"📊 Status Code: {delete_response.status_code}")
        print(f"📄 Response Headers: {dict(delete_response.headers)}")
        print(f"📝 Response Text: {delete_response.text}")
        
        if delete_response.status_code == 200:
            print("✅ RNC deletada com sucesso!")
        else:
            print(f"❌ Erro ao deletar RNC: {delete_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão: Servidor não está rodando ou não acessível")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_delete_rnc() 