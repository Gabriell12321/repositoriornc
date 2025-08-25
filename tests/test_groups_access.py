#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_groups_access():
    """Testar acesso aos grupos para diferentes usuários"""
    
    # Usuários de teste de diferentes departamentos
    test_users = [
        {'email': 'engenharia@teste.com', 'password': 'teste123', 'dept': 'Engenharia'},
        {'email': 'qualidade@teste.com', 'password': 'teste123', 'dept': 'Qualidade'},
        {'email': 'admin@teste.com', 'password': 'teste123', 'dept': 'Administração'},
    ]
    
    print("🔐 TESTE DE ACESSO A GRUPOS E USUÁRIOS")
    print("=" * 60)
    
    base_url = 'http://192.168.3.11:5001'
    
    for user in test_users:
        print(f"\n👤 Testando usuário: {user['email']} ({user['dept']})")
        print("-" * 50)
        
        # Fazer login
        session = requests.Session()
        login_response = session.post(f'{base_url}/login', data={
            'email': user['email'],
            'password': user['password']
        })
        
        if login_response.status_code != 200:
            print(f"❌ Falha no login: {login_response.status_code}")
            continue
        
        print("✅ Login realizado com sucesso")
        
        # Testar acesso aos grupos
        groups_response = session.get(f'{base_url}/api/groups')
        if groups_response.status_code == 200:
            data = groups_response.json()
            if data['success']:
                print(f"✅ Acesso aos grupos: {len(data['groups'])} grupos encontrados")
                for group in data['groups'][:3]:  # Mostrar apenas os 3 primeiros
                    print(f"   - {group['name']}")
            else:
                print(f"❌ Erro ao acessar grupos: {data['message']}")
        else:
            print(f"❌ Falha no acesso aos grupos: {groups_response.status_code}")
        
        # Testar acesso aos usuários
        users_response = session.get(f'{base_url}/api/users/list')
        if users_response.status_code == 200:
            data = users_response.json()
            if data['success']:
                print(f"✅ Acesso aos usuários: {len(data['users'])} usuários encontrados")
                for user_info in data['users'][:3]:  # Mostrar apenas os 3 primeiros
                    print(f"   - {user_info['name']} ({user_info['department']})")
            else:
                print(f"❌ Erro ao acessar usuários: {data['message']}")
        else:
            print(f"❌ Falha no acesso aos usuários: {users_response.status_code}")
        
        # Testar informações do usuário
        user_info_response = session.get(f'{base_url}/api/user/info')
        if user_info_response.status_code == 200:
            data = user_info_response.json()
            if data['success']:
                perms = data['user']['departmentPermissions']
                print(f"✅ Permissões do usuário:")
                print(f"   - Ver grupos para atribuição: {perms.get('canViewGroupsForAssignment', False)}")
                print(f"   - Ver usuários para atribuição: {perms.get('canViewUsersForAssignment', False)}")
            else:
                print(f"❌ Erro ao obter info do usuário: {data['message']}")
        else:
            print(f"❌ Falha ao obter info do usuário: {user_info_response.status_code}")

if __name__ == '__main__':
    test_groups_access()
