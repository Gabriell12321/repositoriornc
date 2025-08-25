#!/usr/bin/env python3
"""
Script para testar o sistema de grupos e permissões
"""

import requests
import json
import time
from datetime import datetime

def test_groups_system():
    """Testa o sistema de grupos e permissões"""
    print("🏢 Testando Sistema de Grupos e Permissões...")
    
    # URL base do servidor
    base_url = "http://localhost:5000"
    
    # 1. Testar login como admin
    print("\n1️⃣ Testando login como admin...")
    
    try:
        session = requests.Session()
        response = session.post(f"{base_url}/api/login", json={
            "email": "admin@ippel.com",
            "password": "admin123"
        })
        
        if response.status_code == 200:
            print("✅ Login admin realizado com sucesso")
        else:
            print(f"❌ Erro no login admin: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com o servidor: {e}")
        return False
    
    # 2. Testar API de grupos
    print("\n2️⃣ Testando API de grupos...")
    
    try:
        response = session.get(f"{base_url}/api/admin/groups")
        
        if response.status_code == 200:
            data = response.json()
            groups = data.get('groups', [])
            print(f"✅ {len(groups)} grupos encontrados")
            
            # Verificar se os grupos corretos existem
            expected_groups = [
                'Produção', 'Engenharia', 'Terceiros', 'Compras', 
                'Comercial', 'PCP', 'Expedição', 'Qualidade'
            ]
            
            found_groups = [group['name'] for group in groups]
            print("📋 Grupos encontrados:")
            for group in groups:
                print(f"   - {group['name']}: {group['description']}")
            
            missing_groups = set(expected_groups) - set(found_groups)
            if missing_groups:
                print(f"⚠️ Grupos faltando: {missing_groups}")
            else:
                print("✅ Todos os grupos esperados foram encontrados")
                
        else:
            print(f"❌ Erro na API de grupos: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar grupos: {e}")
    
    # 3. Testar permissões de grupos
    print("\n3️⃣ Testando permissões de grupos...")
    
    try:
        # Obter lista de grupos
        response = session.get(f"{base_url}/api/admin/groups")
        if response.status_code == 200:
            groups = response.json().get('groups', [])
            
            for group in groups[:3]:  # Testar apenas os primeiros 3 grupos
                group_id = group['id']
                group_name = group['name']
                
                print(f"\n   🔐 Testando permissões do grupo: {group_name}")
                
                # Obter permissões do grupo
                perm_response = session.get(f"{base_url}/api/admin/groups/{group_id}/permissions")
                
                if perm_response.status_code == 200:
                    perm_data = perm_response.json()
                    permissions = perm_data.get('permissions', {})
                    
                    print(f"   ✅ {len(permissions)} permissões encontradas:")
                    for perm_name, perm_value in permissions.items():
                        status = "✅" if perm_value else "❌"
                        print(f"      {status} {perm_name}")
                else:
                    print(f"   ❌ Erro ao obter permissões: {perm_response.status_code}")
                    
        else:
            print(f"❌ Erro ao obter grupos: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar permissões: {e}")
    
    # 4. Testar permissões do usuário
    print("\n4️⃣ Testando permissões do usuário...")
    
    try:
        response = session.get(f"{base_url}/api/user/permissions")
        
        if response.status_code == 200:
            data = response.json()
            permissions = data.get('permissions', [])
            print(f"✅ {len(permissions)} permissões do usuário encontradas")
            
            if 'all' in permissions:
                print("👑 Usuário tem acesso total (admin)")
            else:
                print("📋 Permissões específicas:")
                for perm in permissions:
                    print(f"   - {perm}")
        else:
            print(f"❌ Erro ao obter permissões do usuário: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar permissões do usuário: {e}")
    
    # 5. Testar login com diferentes grupos
    print("\n5️⃣ Testando login com diferentes grupos...")
    
    test_accounts = [
        {"email": "producao@ippel.com", "password": "prod123", "group": "Produção"},
        {"email": "engenharia@ippel.com", "password": "eng123", "group": "Engenharia"},
        {"email": "qualidade@ippel.com", "password": "qual123", "group": "Qualidade"}
    ]
    
    for account in test_accounts:
        print(f"\n   🔐 Testando: {account['group']}")
        
        try:
            # Login
            login_response = session.post(f"{base_url}/api/login", json={
                "email": account["email"],
                "password": account["password"]
            })
            
            if login_response.status_code == 200:
                print(f"   ✅ Login {account['group']} funcionando")
                
                # Obter permissões
                perm_response = session.get(f"{base_url}/api/user/permissions")
                if perm_response.status_code == 200:
                    perm_data = perm_response.json()
                    user_permissions = perm_data.get('permissions', [])
                    print(f"   📋 {len(user_permissions)} permissões: {user_permissions[:3]}...")
                else:
                    print(f"   ⚠️ Erro ao obter permissões")
            else:
                print(f"   ❌ Login {account['group']} falhou")
                
        except Exception as e:
            print(f"   ❌ Erro ao testar {account['group']}: {e}")
    
    print("\n🎯 Teste do sistema de grupos concluído!")
    return True

def test_permission_system():
    """Testa o sistema de permissões específico"""
    print("\n🔐 Testando Sistema de Permissões...")
    
    base_url = "http://localhost:5000"
    
    try:
        session = requests.Session()
        
        # Login como admin
        response = session.post(f"{base_url}/api/login", json={
            "email": "admin@ippel.com",
            "password": "admin123"
        })
        
        if response.status_code != 200:
            print("❌ Falha no login para teste de permissões")
            return
        
        # Testar diferentes funcionalidades baseadas em permissões
        print("\n📋 Testando funcionalidades por permissão:")
        
        # 1. Testar criação de RNC
        print("   🔧 Testando criação de RNC...")
        rnc_data = {
            "title": "Teste RNC - Sistema de Grupos",
            "description": "RNC de teste para verificar permissões",
            "equipment": "Equipamento Teste",
            "client": "Cliente Teste",
            "priority": "Média"
        }
        
        create_response = session.post(f"{base_url}/api/rnc/create", json=rnc_data)
        if create_response.status_code == 200:
            print("   ✅ Criação de RNC permitida")
            rnc_id = create_response.json().get('rnc_id')
        else:
            print(f"   ❌ Criação de RNC negada: {create_response.status_code}")
            rnc_id = None
        
        # 2. Testar listagem de RNCs
        print("   📋 Testando listagem de RNCs...")
        list_response = session.get(f"{base_url}/api/rnc/list")
        if list_response.status_code == 200:
            print("   ✅ Listagem de RNCs permitida")
        else:
            print(f"   ❌ Listagem de RNCs negada: {list_response.status_code}")
        
        # 3. Testar acesso a gráficos
        print("   📊 Testando acesso a gráficos...")
        charts_response = session.get(f"{base_url}/api/charts/data?period=30")
        if charts_response.status_code == 200:
            print("   ✅ Acesso a gráficos permitido")
        else:
            print(f"   ❌ Acesso a gráficos negado: {charts_response.status_code}")
        
        # 4. Testar acesso ao chat
        print("   💬 Testando acesso ao chat...")
        chat_response = session.get(f"{base_url}/chat")
        if chat_response.status_code == 200:
            print("   ✅ Acesso ao chat permitido")
        else:
            print(f"   ❌ Acesso ao chat negado: {chat_response.status_code}")
        
        # 5. Testar acesso administrativo
        print("   👑 Testando acesso administrativo...")
        admin_response = session.get(f"{base_url}/api/admin/users")
        if admin_response.status_code == 200:
            print("   ✅ Acesso administrativo permitido")
        else:
            print(f"   ❌ Acesso administrativo negado: {admin_response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro no teste de permissões: {e}")

def test_group_permissions_structure():
    """Testa a estrutura de permissões dos grupos"""
    print("\n🏗️ Testando Estrutura de Permissões...")
    
    # Definir permissões esperadas para cada grupo
    expected_permissions = {
        'Produção': [
            'create_rnc', 'edit_own_rnc', 'view_own_rnc', 'delete_own_rnc',
            'view_all_rncs', 'finalize_rnc', 'assign_rnc', 'chat_access'
        ],
        'Engenharia': [
            'create_rnc', 'edit_own_rnc', 'view_own_rnc', 'delete_own_rnc',
            'view_all_rncs', 'edit_all_rncs', 'finalize_rnc', 'assign_rnc',
            'chat_access', 'technical_analysis'
        ],
        'Terceiros': [
            'view_own_rnc', 'chat_access', 'limited_access'
        ],
        'Compras': [
            'create_rnc', 'edit_own_rnc', 'view_own_rnc', 'view_all_rncs',
            'chat_access', 'purchase_analysis'
        ],
        'Comercial': [
            'create_rnc', 'edit_own_rnc', 'view_own_rnc', 'view_all_rncs',
            'chat_access', 'commercial_analysis'
        ],
        'PCP': [
            'create_rnc', 'edit_own_rnc', 'view_own_rnc', 'view_all_rncs',
            'edit_all_rncs', 'finalize_rnc', 'assign_rnc', 'chat_access',
            'planning_control'
        ],
        'Expedição': [
            'view_own_rnc', 'view_all_rncs', 'chat_access', 'shipping_access'
        ],
        'Qualidade': [
            'create_rnc', 'edit_own_rnc', 'view_own_rnc', 'delete_own_rnc',
            'view_all_rncs', 'edit_all_rncs', 'finalize_rnc', 'assign_rnc',
            'chat_access', 'quality_control', 'admin_access'
        ]
    }
    
    print("📋 Estrutura de permissões por grupo:")
    for group_name, permissions in expected_permissions.items():
        print(f"\n🏢 {group_name}:")
        for perm in permissions:
            print(f"   - {perm}")
    
    print(f"\n📊 Resumo:")
    print(f"   - Total de grupos: {len(expected_permissions)}")
    total_permissions = sum(len(perms) for perms in expected_permissions.values())
    print(f"   - Total de permissões: {total_permissions}")
    
    # Análise de permissões
    all_permissions = set()
    for perms in expected_permissions.values():
        all_permissions.update(perms)
    
    print(f"   - Permissões únicas: {len(all_permissions)}")
    print(f"   - Lista completa: {sorted(all_permissions)}")

if __name__ == "__main__":
    print("🚀 Iniciando testes do sistema de grupos e permissões")
    print("=" * 70)
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print("✅ Servidor está rodando")
    except:
        print("❌ Servidor não está rodando. Inicie o servidor primeiro!")
        exit(1)
    
    # Executar testes
    test_groups_system()
    test_permission_system()
    test_group_permissions_structure()
    
    print("\n🎉 Testes concluídos!")
    print("\n💡 Para testar o sistema de grupos no navegador:")
    print("   1. Acesse: http://localhost:5000/dashboard")
    print("   2. Faça login como admin")
    print("   3. Vá para 'Gerenciar Usuários'")
    print("   4. Teste a criação de usuários em diferentes grupos")
    print("   5. Verifique as permissões de cada grupo") 