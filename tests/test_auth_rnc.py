#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de autenticação e carregamento de RNCs
"""

import requests
import json

def test_login_and_rncs():
    print("Testando login e carregamento de RNCs...")
    
    base_url = "http://192.168.3.11:5001"
    
    # Criar sessão
    session = requests.Session()
    
    try:
        # Fazer login
        login_data = {
            'email': 'admin@ippel.com.br',
            'password': 'admin123'
        }
        
        print("Fazendo login...")
        response = session.post(f"{base_url}/api/login", json=login_data, timeout=10)
        print(f"Login status: {response.status_code}")
        
        if response.status_code == 200:
            print("Login realizado com sucesso!")
            
            # Testar carregamento de RNCs
            print("Carregando RNCs...")
            rnc_response = session.get(f"{base_url}/api/rnc/list", timeout=10)
            print(f"RNC API status: {rnc_response.status_code}")
            
            if rnc_response.status_code == 200:
                data = rnc_response.json()
                print(f"Sucesso: {data.get('success', False)}")
                print(f"Total de RNCs: {len(data.get('rncs', []))}")
                
                # Mostrar algumas RNCs
                rncs = data.get('rncs', [])
                if rncs:
                    print("Primeiras 3 RNCs:")
                    for i, rnc in enumerate(rncs[:3]):
                        print(f"  {i+1}. {rnc.get('rnc_number', 'N/A')} - {rnc.get('title', 'N/A')}")
                else:
                    print("Nenhuma RNC encontrada")
                    
                return True
            else:
                print(f"Erro na API RNC: {rnc_response.text}")
                return False
        else:
            print(f"Erro no login: {response.text}")
            return False
            
    except Exception as e:
        print(f"Erro: {e}")
        return False

if __name__ == "__main__":
    test_login_and_rncs()
