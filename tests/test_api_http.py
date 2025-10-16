#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste real da API fazendo requisição HTTP
"""
import urllib.request
import json

API_URL = 'http://192.168.3.11:5001/api/admin/clients'

def test_real_api():
    """Testa a API real via HTTP"""
    print("🌐 TESTE REAL DA API via HTTP")
    print("=" * 70)
    print(f"📡 URL: {API_URL}\n")
    
    try:
        # Fazer requisição real
        req = urllib.request.Request(API_URL)
        
        print("🔄 Fazendo requisição...")
        response = urllib.request.urlopen(req, timeout=5)
        
        # Ler resposta
        data = response.read()
        json_data = json.loads(data.decode('utf-8'))
        
        print(f"✅ Status Code: {response.status}")
        print(f"✅ Resposta recebida\n")
        
        if json_data.get('success'):
            clients = json_data.get('clients', [])
            print(f"✅ success: True")
            print(f"✅ Total de clientes retornados: {len(clients)}\n")
            
            if clients:
                print("📝 Primeiros 10 clientes recebidos:")
                print("-" * 70)
                for i, client in enumerate(clients[:10], 1):
                    print(f"{i:2d}. ID: {client['id']:3d} | Nome: {client['name']}")
                print("\n✅ API ESTÁ FUNCIONANDO CORRETAMENTE!")
            else:
                print("⚠️ API retornou lista vazia de clientes")
        else:
            print(f"❌ success: False")
            print(f"❌ Mensagem: {json_data.get('message', 'Sem mensagem')}")
            
    except urllib.error.HTTPError as e:
        print(f"❌ ERRO HTTP {e.code}: {e.reason}")
        print(f"   URL: {API_URL}")
        print(f"\n   Possíveis causas:")
        print(f"   - Servidor Flask não está rodando")
        print(f"   - Rota /api/admin/clients não existe")
        print(f"   - Permissão negada (401/403)")
        
    except urllib.error.URLError as e:
        print(f"❌ ERRO DE CONEXÃO: {e.reason}")
        print(f"   URL: {API_URL}")
        print(f"\n   Possíveis causas:")
        print(f"   - Servidor Flask não está rodando na porta 5001")
        print(f"   - IP 192.168.3.11 não está acessível")
        print(f"   - Firewall bloqueando conexão")
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_real_api()
