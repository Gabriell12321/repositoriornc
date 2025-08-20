#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_api():
    try:
        # Testar API de funcionários
        response = requests.get('http://127.0.0.1:5001/api/employee-performance')
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Dados de funcionários:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"Erro: {response.text}")
            
    except Exception as e:
        print(f'Erro na requisição: {e}')

if __name__ == '__main__':
    test_api()
