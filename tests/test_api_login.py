#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_api_with_login():
    session = requests.Session()
    
    # Fazer login primeiro
    login_data = {
        'email': 'admin@ippel.com.br',
        'password': 'admin123'
    }
    
    try:
        # Login
        response = session.post('http://192.168.3.11:5001/api/login', json=login_data)
        login_result = response.json()
        
        if not login_result.get('success'):
            print(f'Erro no login: {login_result}')
            return
            
        print('✅ Login realizado com sucesso')
        
        # Buscar RNCs finalizadas
        response = session.get('http://192.168.3.11:5001/api/rnc/list?tab=finalized')
        data = response.json()
        
        if data.get('success') and data.get('rncs'):
            print(f'Total RNCs finalizadas: {len(data["rncs"])}')
            print('\nPrimeiras 3 RNCs:')
            for i, rnc in enumerate(data['rncs'][:3]):
                print(f'  {i+1}. RNC {rnc.get("id")}: {rnc.get("title", "Sem título")[:30]}')
                print(f'     Setor: {rnc.get("department", "N/A")} | User Dept: {rnc.get("user_department", "N/A")}')
                print(f'     Status: {rnc.get("status")} | Criador: {rnc.get("user_name")}')
                print()
        else:
            print('Erro na resposta:', data)
            
    except Exception as e:
        print(f'Erro na requisição: {e}')

if __name__ == '__main__':
    test_api_with_login()
