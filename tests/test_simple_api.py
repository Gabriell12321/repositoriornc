#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script simples para testar a API de performance
"""

import requests
import json

def test_api():
    """Testa a API de performance"""
    print("🧪 Testando API de performance...")
    
    # URL da API (ajuste conforme necessário)
    url = "http://localhost:5001/api/test/performance"
    
    try:
        # Fazer requisição GET
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API funcionando!")
            print(f"📊 Total de usuários: {data.get('total_users', 0)}")
            print(f"📈 RNCs encontradas: {data.get('total_rncs_found', 0)}")
            
            # Mostrar diagnóstico
            if 'diagnostic' in data:
                diag = data['diagnostic']
                print(f"\n🔍 Diagnóstico:")
                print(f"   Total no banco: {diag.get('total_users_db', 0)}")
                print(f"   Usuários ativos: {diag.get('active_users_db', 0)}")
                print(f"   Com nome: {diag.get('named_users_db', 0)}")
                print(f"   Encontrados na consulta: {diag.get('users_found_in_query', 0)}")
                print(f"   Com RNCs: {diag.get('users_with_rncs', 0)}")
                print(f"   Sem RNCs: {diag.get('users_without_rncs', 0)}")
            
            # Mostrar alguns usuários
            if 'data' in data and data['data']:
                print(f"\n👥 Primeiros 10 usuários:")
                for user in data['data'][:10]:
                    print(f"   ID {user['id']}: {user['name']} - {user['rncs']} RNCs - {user['status']}")
            
            # Mostrar debug
            if 'debug' in data:
                debug = data['debug']
                print(f"\n🐛 Debug:")
                print(f"   Usuários processados: {debug.get('users_processed', 0)}")
                print(f"   RNCs por usuário: {debug.get('rnc_data', {})}")
                print(f"   Usuários sem RNCs: {debug.get('users_without_rncs', [])}")
                
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar com o servidor")
        print("   Verifique se o servidor está rodando na porta 5001")
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")

if __name__ == "__main__":
    test_api()
