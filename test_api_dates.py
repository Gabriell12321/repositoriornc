#!/usr/bin/env python3
"""Teste da API para verificar se as datas estão sendo retornadas."""

import requests
import json

try:
    # Testar a API diretamente
    response = requests.get('http://localhost:5001/api/rnc/list?tab=active&limit=2')
    
    if response.status_code == 200:
        data = response.json()
        if data.get('rncs'):
            print("✅ API funcionando!")
            print(f"Total de RNCs: {len(data['rncs'])}")
            print("\n📅 Primeiro RNC:")
            first_rnc = data['rncs'][0]
            print(json.dumps(first_rnc, indent=2, ensure_ascii=False))
            
            # Verificar especificamente a data
            created_at = first_rnc.get('created_at')
            print(f"\n🗓️ Campo created_at: {created_at}")
            print(f"Tipo: {type(created_at)}")
            
            if created_at:
                print("✅ Data presente na API!")
            else:
                print("❌ Data não presente na API!")
        else:
            print("❌ Nenhuma RNC retornada")
    else:
        print(f"❌ Erro na API: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"❌ Erro: {e}")