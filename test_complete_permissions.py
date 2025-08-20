#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Completo do Sistema de Permissões por Grupo
"""
import requests
import json
import time

def test_complete_group_permissions():
    """Teste completo do sistema de permissões por grupo"""
    print("🔧 TESTE COMPLETO DO SISTEMA DE PERMISSÕES POR GRUPO")
    print("=" * 70)
    
    base_url = "http://192.168.3.11:5001"  # URL do servidor
    
    # Dados de teste para diferentes grupos
    test_users = [
        {
            'group': 'TI',
            'email': 'admin@ippel.com.br',
            'password': 'admin123',
            'expected_permissions': ['admin_access', 'view_all_rncs', 'view_charts', 'manage_users']
        },
        {
            'group': 'Qualidade', 
            'email': 'ronaldo@ippel.com.br',
            'password': 'teste123',
            'expected_permissions': ['view_all_rncs', 'view_charts', 'quality_control']
        },
        {
            'group': 'Engenharia',
            'email': 'engenharia@1',
            'password': 'teste123', 
            'expected_permissions': ['view_own_rncs', 'create_rnc', 'technical_analysis']
        }
    ]
    
    for i, user_data in enumerate(test_users, 1):
        print(f"\n🧪 TESTE {i}: Grupo {user_data['group']}")
        print("-" * 50)
        
        try:
            # 1. Fazer login
            session = requests.Session()
            login_response = session.post(f"{base_url}/api/login", json={
                'email': user_data['email'],
                'password': user_data['password']
            })
            
            if login_response.status_code != 200:
                print(f"❌ Falha no login: {login_response.status_code}")
                continue
            
            print(f"✅ Login realizado: {user_data['email']}")
            
            # 2. Obter informações do usuário
            print("\n📋 Informações do usuário:")
            user_info_response = session.get(f"{base_url}/api/user/info")
            
            if user_info_response.status_code == 200:
                user_info = user_info_response.json()
                if user_info['success']:
                    user = user_info['user']
                    print(f"   👤 Nome: {user['name']}")
                    print(f"   🏢 Grupo: {user.get('group', 'N/A')}")
                    print(f"   🏛️ Departamento: {user['department']}")
                    print(f"   🔑 Permissões do grupo: {len(user.get('groupPermissions', []))}")
                    
                    # Mostrar algumas permissões
                    group_perms = user.get('groupPermissions', [])
                    if group_perms:
                        print(f"   📜 Primeiras permissões: {group_perms[:5]}")
                        
                        # Verificar se tem permissões esperadas
                        has_expected = any(perm in group_perms for perm in user_data['expected_permissions'])
                        status = "✅" if has_expected else "⚠️"
                        print(f"   {status} Permissões esperadas encontradas: {has_expected}")
                    
                    # Verificar permissões específicas
                    dept_perms = user.get('departmentPermissions', {})
                    print(f"   🎯 Pode ver todos RNCs: {dept_perms.get('canViewAllRncs', False)}")
                    print(f"   📊 Pode ver gráficos: {dept_perms.get('canViewCharts', False)}")
                    print(f"   👑 Acesso admin: {dept_perms.get('hasAdminAccess', False)}")
            
            # 3. Testar acesso a RNCs
            print("\n📁 Teste de acesso a RNCs:")
            rnc_response = session.get(f"{base_url}/api/rnc/list?tab=active")
            
            if rnc_response.status_code == 200:
                rnc_data = rnc_response.json()
                if rnc_data['success']:
                    rncs = rnc_data['rncs']
                    print(f"   ✅ Pode acessar RNCs ativos: {len(rncs)} encontrados")
                else:
                    print(f"   ❌ Erro ao acessar RNCs: {rnc_data['message']}")
            else:
                print(f"   ❌ Falha no acesso a RNCs: {rnc_response.status_code}")
            
            # 4. Testar acesso a gráficos
            print("\n📊 Teste de acesso a gráficos:")
            charts_response = session.get(f"{base_url}/api/charts/data?period=30")
            
            if charts_response.status_code == 200:
                print("   ✅ Pode acessar gráficos")
            elif charts_response.status_code == 403:
                print("   ❌ Acesso a gráficos negado (sem permissão)")
            else:
                print(f"   ⚠️ Erro no acesso a gráficos: {charts_response.status_code}")
            
            # 5. Testar acesso administrativo
            print("\n👑 Teste de acesso administrativo:")
            admin_response = session.get(f"{base_url}/api/admin/users")
            
            if admin_response.status_code == 200:
                print("   ✅ Tem acesso administrativo")
            elif admin_response.status_code == 403:
                print("   ❌ Acesso administrativo negado")
            else:
                print(f"   ⚠️ Erro no acesso admin: {admin_response.status_code}")
            
            # 6. Testar permissões específicas do grupo
            print("\n🔐 Teste de permissões específicas:")
            group_perms_response = session.get(f"{base_url}/api/user/group-permissions")
            
            if group_perms_response.status_code == 200:
                perms_data = group_perms_response.json()
                if perms_data['success']:
                    permissions = perms_data['permissions']
                    print(f"   🔑 Total de permissões: {len(permissions)}")
                    print(f"   📊 Pode ver gráficos: {perms_data['can_view_charts']}")
                    print(f"   📁 Pode ver todos RNCs: {perms_data['can_view_all_rncs']}")
                    print(f"   👑 Acesso admin: {perms_data['has_admin_access']}")
            
        except Exception as e:
            print(f"❌ Erro no teste do grupo {user_data['group']}: {e}")
    
    print("\n🎉 TESTE COMPLETO FINALIZADO!")
    print("=" * 70)

def test_permission_filtering():
    """Testar filtragem específica de dados"""
    print("\n🔍 TESTE DE FILTRAGEM POR PERMISSÕES")
    print("-" * 50)
    
    base_url = "http://192.168.3.11:5001"
    
    # Login como usuário de Engenharia (permissões limitadas)
    session = requests.Session()
    login_response = session.post(f"{base_url}/api/login", json={
        'email': 'engenharia@1',
        'password': 'teste123'
    })
    
    if login_response.status_code == 200:
        print("✅ Login como Engenharia realizado")
        
        # Testar diferentes endpoints e verificar filtragem
        endpoints = [
            ('/api/rnc/list?tab=active', 'RNCs Ativos'),
            ('/api/rnc/list?tab=finalized', 'RNCs Finalizados'),
            ('/api/charts/data', 'Dados de Gráficos'),
            ('/api/users', 'Lista de Usuários')
        ]
        
        for endpoint, name in endpoints:
            print(f"\n🔍 Testando {name}: {endpoint}")
            response = session.get(f"{base_url}{endpoint}")
            
            if response.status_code == 200:
                print(f"   ✅ Acesso permitido")
                try:
                    data = response.json()
                    if 'rncs' in data:
                        print(f"   📁 {len(data['rncs'])} RNCs retornados")
                    elif 'users' in data:
                        print(f"   👥 {len(data['users'])} usuários retornados")
                    else:
                        print(f"   📊 Dados de gráfico retornados")
                except:
                    print(f"   📄 Resposta não-JSON")
            elif response.status_code == 403:
                print(f"   ❌ Acesso negado (filtrado por permissão)")
            else:
                print(f"   ⚠️ Erro: {response.status_code}")
    else:
        print("❌ Falha no login para teste de filtragem")

if __name__ == "__main__":
    test_complete_group_permissions()
    test_permission_filtering()
