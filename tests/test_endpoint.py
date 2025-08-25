#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Teste direto do endpoint de engenharia"""

import requests
import json

def test_endpoint():
    try:
        # Fazer login primeiro
        login_data = {
            'email': 'admin@ippel.com.br',
            'password': 'admin123'
        }
        
        session = requests.Session()
        
        # Login
        login_resp = session.post('http://127.0.0.1:5001/api/login', json=login_data)
        print(f"Login status: {login_resp.status_code}")
        
        if login_resp.status_code == 200:
            # Testar endpoint de engenharia
            eng_resp = session.get('http://127.0.0.1:5001/api/indicadores/engenharia')
            print(f"Engineering endpoint status: {eng_resp.status_code}")
            
            if eng_resp.status_code == 200:
                data = eng_resp.json()
                print("✅ Engineering endpoint response:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                print(f"❌ Engineering endpoint error: {eng_resp.text}")
        else:
            print(f"❌ Login failed: {login_resp.text}")
            
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_endpoint()
