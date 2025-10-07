#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testa a API real do servidor Flask em execução
"""
import requests
import json

# URL do servidor
BASE_URL = "http://192.168.3.11:5001"
API_ENDPOINT = f"{BASE_URL}/api/admin/clients"

print("🌐 TESTE DA API REAL DO SERVIDOR FLASK")
print("=" * 70)
print(f"   🔗 Endpoint: {API_ENDPOINT}")
print("=" * 70)

try:
    print("\n📡 Fazendo requisição GET...")
    
    # Fazer requisição (sem autenticação - pode falhar com 401)
    response = requests.get(API_ENDPOINT, timeout=5)
    
    print(f"   📊 Status Code: {response.status_code}")
    print(f"   📦 Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n   ✅ SUCESSO! API respondeu corretamente")
        print(f"   📄 Resposta JSON:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if data.get('success'):
            clients = data.get('clients', [])
            print(f"\n   ✅ Total de clientes na resposta: {len(clients)}")
            if len(clients) > 0:
                print(f"   📝 Primeiros 3 clientes:")
                for i, client in enumerate(clients[:3], 1):
                    print(f"      {i}. {client}")
            else:
                print(f"   ⚠️  Lista de clientes está VAZIA!")
        else:
            print(f"   ❌ API retornou success=false: {data.get('message')}")
            
    elif response.status_code == 401:
        print(f"\n   🔐 ERRO 401: Não autenticado")
        print(f"   💡 Isso é esperado - você precisa estar logado no navegador")
        print(f"   ℹ️  O problema NÃO é com a API, mas com autenticação")
        
    elif response.status_code == 403:
        print(f"\n   🚫 ERRO 403: Acesso negado")
        print(f"   💡 Usuário não tem permissão para acessar esta API")
        print(f"   ℹ️  Certifique-se de estar logado como administrador")
        
    else:
        print(f"\n   ❌ ERRO: Status {response.status_code}")
        print(f"   📄 Resposta: {response.text}")
        
except requests.exceptions.ConnectionError:
    print(f"\n   ❌ ERRO DE CONEXÃO!")
    print(f"   💡 O servidor Flask NÃO está respondendo em {BASE_URL}")
    print(f"   🔧 SOLUÇÃO: Certifique-se de que o servidor está rodando")
    
except requests.exceptions.Timeout:
    print(f"\n   ⏱️  TIMEOUT!")
    print(f"   💡 O servidor demorou muito para responder")
    
except Exception as e:
    print(f"\n   ❌ ERRO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("💡 PRÓXIMOS PASSOS:")
print("   1. Se você viu ERRO 401/403: Abra o navegador e teste lá")
print("   2. No navegador, pressione F12 e vá para a aba 'Network'")
print("   3. Recarregue a página /admin/clients")
print("   4. Procure pela requisição 'clients' e veja o Status e Response")
