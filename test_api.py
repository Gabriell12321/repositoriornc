#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

print("=== TESTE DAS APIS DE FILTROS ===")

base_url = "http://127.0.0.1:5001"

# Testar sem autenticação primeiro (pode dar erro de autorização)
print("\n🔍 Testando API de RNC...")
try:
    response = requests.get(f"{base_url}/api/indicadores-detalhados?tipo=rnc", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Dados recebidos: {list(data.keys())}")
        if 'monthlyData' in data:
            print(f"   📊 Meses: {len(data['monthlyData'])}")
        if 'departments' in data:
            print(f"   🏢 Departamentos: {len(data['departments'])}")
    else:
        print(f"   ❌ Erro: {response.text}")
except Exception as e:
    print(f"   ❌ Erro de conexão: {e}")

print("\n🔍 Testando API de GARANTIA...")
try:
    response = requests.get(f"{base_url}/api/indicadores-detalhados?tipo=garantia", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Dados recebidos: {list(data.keys())}")
        if 'monthlyData' in data:
            print(f"   📊 Meses: {len(data['monthlyData'])}")
        if 'departments' in data:
            print(f"   🏢 Departamentos: {len(data['departments'])}")
    else:
        print(f"   ❌ Erro: {response.text}")
except Exception as e:
    print(f"   ❌ Erro de conexão: {e}")

print("\n✅ Teste das APIs concluído!")
