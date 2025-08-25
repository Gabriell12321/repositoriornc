#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste das APIs de Gerenciamento de Permissões
"""
import requests
import json
import time

def test_permission_apis():
    """Testa as APIs de concessão e revogação de permissões"""
    base_url = "http://127.0.0.1:5001"
    
    print("🔧 Testando APIs de Gerenciamento de Permissões")
    print("=" * 60)
    
    # Dados de login admin
    login_data = {
        "email": "admin@ippel.com.br",
        "password": "admin123"
    }
    
    try:
        # 1. Fazer login como admin
        print("\n1. Fazendo login como admin...")
        session = requests.Session()
        response = session.post(f"{base_url}/login", data=login_data)
        
        if response.status_code == 200:
            print("   ✅ Login realizado com sucesso")
        else:
            print(f"   ❌ Erro no login: {response.status_code}")
            return
        
        # 2. Listar usuários disponíveis
        print("\n2. Listando usuários...")
        response = session.get(f"{base_url}/api/users")
        
        if response.status_code == 200:
            users = response.json()
            print(f"   ✅ {len(users)} usuários encontrados")
            
            # Encontrar um usuário de teste (não admin)
            test_user = None
            for user in users:
                if user['email'] != 'admin@ippel.com.br':
                    test_user = user
                    break
            
            if not test_user:
                print("   ⚠️ Nenhum usuário de teste encontrado")
                return
            
            print(f"   👤 Usuário de teste: {test_user['email']}")
            print(f"   🏢 Departamento: {test_user.get('department', 'N/A')}")
            print(f"   🔑 Permissões atuais: {test_user.get('permissions', [])}")
            
        else:
            print(f"   ❌ Erro ao listar usuários: {response.status_code}")
            return
        
        # 3. Testar concessão de permissão
        print("\n3. Testando concessão de permissão...")
        test_permission = "view_charts"
        
        grant_data = {
            "user_id": test_user['id'],
            "permission": test_permission
        }
        
        response = session.post(f"{base_url}/api/admin/grant-permission", json=grant_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Permissão concedida: {result['message']}")
        else:
            print(f"   ❌ Erro ao conceder permissão: {response.status_code}")
            try:
                error = response.json()
                print(f"      Erro: {error.get('error', 'Desconhecido')}")
            except:
                print(f"      Erro: {response.text}")
        
        # 4. Verificar se a permissão foi adicionada
        print("\n4. Verificando permissão adicionada...")
        time.sleep(1)  # Aguardar um pouco
        
        response = session.get(f"{base_url}/api/users")
        if response.status_code == 200:
            users = response.json()
            updated_user = next((u for u in users if u['id'] == test_user['id']), None)
            
            if updated_user:
                current_perms = updated_user.get('permissions', [])
                if test_permission in current_perms:
                    print(f"   ✅ Permissão encontrada: {test_permission}")
                else:
                    print(f"   ⚠️ Permissão não encontrada nas permissões do usuário")
                print(f"   📝 Permissões atuais: {current_perms}")
        
        # 5. Testar revogação de permissão
        print("\n5. Testando revogação de permissão...")
        
        revoke_data = {
            "user_id": test_user['id'],
            "permission": test_permission
        }
        
        response = session.post(f"{base_url}/api/admin/revoke-permission", json=revoke_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Permissão revogada: {result['message']}")
        else:
            print(f"   ❌ Erro ao revogar permissão: {response.status_code}")
            try:
                error = response.json()
                print(f"      Erro: {error.get('error', 'Desconhecido')}")
            except:
                print(f"      Erro: {response.text}")
        
        # 6. Verificar se a permissão foi removida
        print("\n6. Verificando permissão removida...")
        time.sleep(1)  # Aguardar um pouco
        
        response = session.get(f"{base_url}/api/users")
        if response.status_code == 200:
            users = response.json()
            updated_user = next((u for u in users if u['id'] == test_user['id']), None)
            
            if updated_user:
                current_perms = updated_user.get('permissions', [])
                if test_permission not in current_perms:
                    print(f"   ✅ Permissão removida com sucesso")
                else:
                    print(f"   ⚠️ Permissão ainda presente nas permissões do usuário")
                print(f"   📝 Permissões finais: {current_perms}")
        
        print("\n✅ Teste das APIs concluído!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("   Certifique-se de que o servidor está rodando em http://127.0.0.1:5001")
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_permission_apis()
