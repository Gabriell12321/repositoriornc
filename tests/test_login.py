#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o login no sistema
"""

import requests
import json

def test_login():
    """Testa o login no sistema"""
    
    base_url = "http://172.26.0.196:5001"
    
    print("🔍 Testando login no sistema...")
    print(f"URL: {base_url}")
    
    # Dados de login
    login_data = {
        'email': 'gabriel@admin',
        'password': '123456'
    }
    
    try:
        print(f"\n🔐 Tentando login com: {login_data['email']}")
        
        # Fazer requisição de login
        response = requests.post(f'{base_url}/api/login', json=login_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Login realizado com sucesso!")
            data = response.json()
            print(f"Resposta: {data}")
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"Resposta: {response.text}")
            
            # Tentar com credenciais padrão
            print("\n🔄 Tentando com credenciais padrão...")
            default_data = {
                'email': 'admin@ippel.com.br',
                'password': 'admin123'
            }
            
            response2 = requests.post(f'{base_url}/api/login', json=default_data)
            print(f"Status Code: {response2.status_code}")
            
            if response2.status_code == 200:
                print("✅ Login com credenciais padrão funcionou!")
                data2 = response2.json()
                print(f"Resposta: {data2}")
            else:
                print(f"❌ Login padrão também falhou: {response2.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("Verifique se o servidor está rodando em 172.26.0.196:5001")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_login()
