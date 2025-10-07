#!/usr/bin/env python3
"""Limpar cache e verificar dados."""

import requests
import json

try:
    # Fazer chamada com force refresh
    url = 'http://localhost:5001/api/rnc/list?tab=active&limit=2&_t=force_refresh_now'
    
    # Simular sessão de usuário
    session = requests.Session()
    
    # Tentar fazer login primeiro
    login_response = session.post('http://localhost:5001/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    
    if login_response.status_code == 200:
        print("✅ Login realizado com sucesso")
        
        # Agora fazer a requisição para a API
        api_response = session.get(url)
        
        if api_response.status_code == 200:
            data = api_response.json()
            if data.get('rncs'):
                print(f"✅ API retornou {len(data['rncs'])} RNCs")
                first_rnc = data['rncs'][0]
                print(f"\n📝 Primeiro RNC:")
                print(f"   ID: {first_rnc.get('id')}")
                print(f"   Número: {first_rnc.get('rnc_number')}")
                print(f"   user_name: {first_rnc.get('user_name')}")
                print(f"   Responsável: {first_rnc.get('responsavel', 'CAMPO NÃO EXISTE')}")
            else:
                print("❌ Nenhuma RNC retornada")
        else:
            print(f"❌ Erro na API: {api_response.status_code}")
            print(api_response.text)
    else:
        print(f"❌ Erro no login: {login_response.status_code}")
        
except Exception as e:
    print(f"❌ Erro: {e}")