#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import time

def test_api_response():
    """Testa o formato da resposta da API"""
    
    # Aguardar servidor estar pronto
    time.sleep(1)
    
    try:
        # Testar API de locks do grupo teste (ID=1)
        response = requests.get("http://localhost:5001/admin/field-locks/api/locks/1", timeout=10)
        
        print(f"🔍 Status: {response.status_code}")
        print(f"📋 Headers: {response.headers.get('content-type', 'N/A')}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Resposta JSON:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Analisar estrutura
            if 'locks' in data:
                locks = data['locks']
                print(f"\n🔒 Análise dos locks:")
                print(f"   - Tipo: {type(locks)}")
                print(f"   - Quantidade: {len(locks)}")
                
                # Mostrar alguns exemplos
                count = 0
                for field_name, lock_data in locks.items():
                    if count < 3:  # Mostrar apenas 3 exemplos
                        print(f"   - {field_name}: {lock_data}")
                        count += 1
                    
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não conectado na porta 5001")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_api_response()