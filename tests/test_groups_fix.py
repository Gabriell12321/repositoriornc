#!/usr/bin/env python3
import requests
import json

def test_group_system():
    """Testar sistema de grupos"""
    print("=== TESTE DO SISTEMA DE GRUPOS ===\n")
    
    base_url = "http://127.0.0.1:5000"
    
    # 1. Testar login com admin
    print("1. 🔐 Testando login com administrador...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    session = requests.Session()
    
    try:
        # Login
        response = session.post(f"{base_url}/login", data=login_data)
        if response.status_code == 200:
            print("   ✅ Login realizado com sucesso")
        else:
            print(f"   ❌ Erro no login: {response.status_code}")
            return
        
        # 2. Buscar grupos disponíveis
        print("\n2. 📋 Buscando grupos disponíveis...")
        response = session.get(f"{base_url}/api/admin/groups")
        if response.status_code == 200:
            groups_data = response.json()
            if groups_data.get('success'):
                groups = groups_data.get('groups', [])
                print(f"   ✅ {len(groups)} grupos encontrados:")
                for group in groups:
                    print(f"     - ID {group['id']}: {group['name']}")
            else:
                print(f"   ❌ Erro na resposta: {groups_data}")
        else:
            print(f"   ❌ Erro ao buscar grupos: {response.status_code}")
        
        # 3. Criar RNC para grupo Engenharia
        print("\n3. 📝 Criando RNC para grupo Engenharia...")
        rnc_data = {
            "title": "Teste RNC Admin para Engenharia",
            "description": "RNC criada pelo admin para testar sistema de grupos",
            "equipment": "Equipamento Teste",
            "client": "Cliente Teste",
            "priority": "Alta",
            "price": 100.50,
            "shared_group_ids": [1],  # ID do grupo Engenharia
            "assinatura1": "Admin Teste",
            "assinatura2": "",
            "assinatura3": ""
        }
        
        response = session.post(f"{base_url}/api/rnc/create", 
                               headers={'Content-Type': 'application/json'},
                               data=json.dumps(rnc_data))
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                rnc_id = result.get('rnc_id')
                print(f"   ✅ RNC criado com sucesso! ID: {rnc_id}")
                
                # 4. Verificar se RNC foi criado com departamento correto
                print("\n4. 🔍 Verificando departamento da RNC criada...")
                debug_response = session.get(f"{base_url}/api/test/groups-debug")
                if debug_response.status_code == 200:
                    debug_data = debug_response.json()
                    print(f"   📊 Dados de debug: {debug_data}")
                
            else:
                print(f"   ❌ Erro ao criar RNC: {result.get('message')}")
        else:
            print(f"   ❌ Erro na requisição: {response.status_code} - {response.text}")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")

if __name__ == "__main__":
    test_group_system()
