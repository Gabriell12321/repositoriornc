#!/usr/bin/env python3
"""Limpar cache via API."""

import requests

try:
    # Limpar cache
    response = requests.post('http://localhost:5001/api/cache/clear')
    
    if response.status_code == 200:
        print("✅ Cache limpo com sucesso!")
        print(response.json())
    else:
        print(f"❌ Erro ao limpar cache: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Erro: {e}")