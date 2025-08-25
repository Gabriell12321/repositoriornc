#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_permission_management():
    """Testar gestão de permissões de usuários"""
    
    base_url = 'http://192.168.3.11:5001'
    
    print("🔐 TESTE DE GESTÃO DE PERMISSÕES")
    print("=" * 50)
    
    # Fazer login como admin
    session = requests.Session()
    login_response = session.post(f'{base_url}/login', data={
        'email': 'admin@ippel.com.br',
        'password': 'admin123'
    })
    
    if login_response.status_code != 200:
        print(f"❌ Falha no login: {login_response.status_code}")
        return
    
    print("✅ Login como admin realizado")
    
    # Listar permissões disponíveis
    perms_response = session.get(f'{base_url}/api/admin/permissions/list')
    if perms_response.status_code == 200:
        data = perms_response.json()
        print(f"✅ {len(data['permissions'])} permissões disponíveis:")
        for perm in data['permissions'][:5]:  # Mostrar apenas as 5 primeiras
            print(f"   - {perm}")
        print("   ...")
    else:
        print(f"❌ Erro ao listar permissões: {perms_response.status_code}")
        return
    
    # Buscar um usuário de teste
    users_response = session.get(f'{base_url}/api/admin/users')
    if users_response.status_code == 200:
        users_data = users_response.json()
        if users_data['success'] and len(users_data['users']) > 1:
            test_user = users_data['users'][1]  # Pegar o segundo usuário
            user_id = test_user['id']
            user_name = test_user['name']
            
            print(f"\n👤 Testando com usuário: {user_name} (ID: {user_id})")
            
            # Tentar conceder uma permissão
            grant_response = session.post(f'{base_url}/api/admin/grant-permission', 
                json={'user_id': user_id, 'permission': 'view_charts'})
            
            if grant_response.status_code == 200:
                grant_data = grant_response.json()
                if grant_data['success']:
                    print(f"✅ Permissão concedida: {grant_data['message']}")
                else:
                    print(f"⚠️ Aviso: {grant_data['message']}")
            else:
                print(f"❌ Erro ao conceder permissão: {grant_response.status_code}")
                if grant_response.headers.get('content-type', '').startswith('application/json'):
                    error_data = grant_response.json()
                    print(f"   Erro: {error_data.get('message', 'Desconhecido')}")
            
            # Tentar remover a permissão
            revoke_response = session.post(f'{base_url}/api/admin/revoke-permission',
                json={'user_id': user_id, 'permission': 'view_charts'})
            
            if revoke_response.status_code == 200:
                revoke_data = revoke_response.json()
                if revoke_data['success']:
                    print(f"✅ Permissão removida: {revoke_data['message']}")
                else:
                    print(f"⚠️ Aviso: {revoke_data['message']}")
            else:
                print(f"❌ Erro ao remover permissão: {revoke_response.status_code}")
                if revoke_response.headers.get('content-type', '').startswith('application/json'):
                    error_data = revoke_response.json()
                    print(f"   Erro: {error_data.get('message', 'Desconhecido')}")
        else:
            print("❌ Não foi possível encontrar usuários para teste")
    else:
        print(f"❌ Erro ao listar usuários: {users_response.status_code}")

if __name__ == '__main__':
    test_permission_management()
