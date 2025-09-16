#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar o sistema de permissões das ações rápidas
"""

import sqlite3
import requests
import json

def test_quick_actions_permissions():
    """Testa o sistema de permissões das ações rápidas."""
    
    print("=" * 70)
    print("TESTE DO SISTEMA DE PERMISSÕES - AÇÕES RÁPIDAS")
    print("=" * 70)
    
    # Verificar estrutura do banco
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    print("\n📊 VERIFICANDO ESTRUTURA DO BANCO:")
    
    # Verificar tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%quick%'")
    tables = cursor.fetchall()
    print(f"✅ Tabelas encontradas: {[t[0] for t in tables]}")
    
    # Verificar ações cadastradas
    cursor.execute("SELECT COUNT(*) FROM quick_actions")
    actions_count = cursor.fetchone()[0]
    print(f"✅ Ações cadastradas: {actions_count}")
    
    # Verificar permissões
    cursor.execute("SELECT COUNT(*) FROM quick_action_permissions")
    permissions_count = cursor.fetchone()[0]
    print(f"✅ Permissões configuradas: {permissions_count}")
    
    # Listar usuários e grupos
    cursor.execute("PRAGMA table_info(users)")
    user_columns = cursor.fetchall()
    print(f"\n📋 COLUNAS DA TABELA USERS:")
    for col in user_columns:
        print(f"  - {col[1]} ({col[2]})")
    
    cursor.execute("SELECT id, name FROM users ORDER BY id")
    users = cursor.fetchall()
    print(f"\n👥 USUÁRIOS DISPONÍVEIS:")
    for user in users:
        print(f"  ID: {user[0]}, Nome: {user[1]}")
    
    cursor.execute("SELECT id, name FROM groups ORDER BY id")
    groups = cursor.fetchall()
    print(f"\n👥 GRUPOS DISPONÍVEIS:")
    for group in groups:
        print(f"  ID: {group[0]}, Nome: {group[1]}")
    
    conn.close()
    
    # Testar API
    print(f"\n🔗 TESTANDO API:")
    base_url = "http://127.0.0.1:5001"
    
    # Testar para cada usuário
    for user in users:
        user_id = user[0]
        username = user[1]
        
        try:
            response = requests.get(f"{base_url}/admin/api/user-quick-actions/{user_id}")
            
            if response.status_code == 200:
                actions = response.json()
                print(f"✅ Usuário {username} (ID: {user_id}):")
                if actions:
                    for action in actions:
                        print(f"    - {action['name']} ({action['key']})")
                else:
                    print(f"    - Nenhuma ação permitida")
            else:
                print(f"❌ Erro para usuário {username}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro de conexão para usuário {username}: {e}")
    
    print(f"\n🌐 ACESSO À INTERFACE:")
    print(f"   📋 Gerenciar Permissões: {base_url}/admin/quick-actions-permissions")
    print(f"   🏠 Dashboard: {base_url}/dashboard")
    
    # Verificar permissões detalhadas
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    print(f"\n📋 PERMISSÕES DETALHADAS:")
    cursor.execute('''
        SELECT qa.action_name, g.name as group_name, qap.permission_level
        FROM quick_action_permissions qap
        JOIN quick_actions qa ON qap.action_key = qa.action_key
        JOIN groups g ON qap.group_id = g.id
        ORDER BY qa.action_name, g.name
    ''')
    
    permissions = cursor.fetchall()
    if permissions:
        for perm in permissions:
            print(f"  🔹 {perm[0]} → Grupo: {perm[1]} ({perm[2]})")
    else:
        print("  ⚠️ Nenhuma permissão configurada")
    
    # Mostrar grupos de cada usuário
    print(f"\n👥 GRUPOS POR USUÁRIO:")
    for user in users:
        user_id = user[0]
        username = user[1]
        
        cursor.execute('''
            SELECT g.name
            FROM user_groups ug
            JOIN groups g ON ug.group_id = g.id
            WHERE ug.user_id = ?
        ''', (user_id,))
        
        user_groups = cursor.fetchall()
        group_names = [g[0] for g in user_groups]
        print(f"  👤 {username}: {group_names if group_names else 'Nenhum grupo'}")
    
    conn.close()
    
    print(f"\n" + "=" * 70)
    print("✅ TESTE CONCLUÍDO!")
    print(f"=" * 70)
    print(f"\n💡 COMO TESTAR:")
    print(f"1. Acesse {base_url}/admin/quick-actions-permissions")
    print(f"2. Configure as permissões para diferentes grupos")
    print(f"3. Acesse {base_url}/dashboard e veja as ações disponíveis")
    print(f"4. Teste com diferentes usuários")

def create_test_permissions():
    """Cria permissões de teste para demonstrar o sistema."""
    
    print("\n" + "=" * 70)
    print("CRIANDO PERMISSÕES DE TESTE")
    print("=" * 70)
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Exemplo: Dar algumas permissões para o grupo Engenharia
    cursor.execute('SELECT id FROM groups WHERE name = "Engenharia"')
    eng_group = cursor.fetchone()
    
    if eng_group:
        test_permissions = [
            ('manage_clients', eng_group[0], 'view'),
            ('manage_areas', eng_group[0], 'view'),
        ]
        
        for action_key, group_id, level in test_permissions:
            cursor.execute('''
                INSERT OR IGNORE INTO quick_action_permissions 
                (action_key, group_id, permission_level)
                VALUES (?, ?, ?)
            ''', (action_key, group_id, level))
        
        print(f"✅ Permissões adicionadas para grupo Engenharia:")
        print(f"   - Cadastro de Clientes")
        print(f"   - Cadastro de Área")
    
    # Exemplo: Dar permissões para o grupo Qualidade
    cursor.execute('SELECT id FROM groups WHERE name = "Qualidade"')
    qual_group = cursor.fetchone()
    
    if qual_group:
        test_permissions = [
            ('generate_report', qual_group[0], 'view'),
            ('employee_expenses', qual_group[0], 'view'),
        ]
        
        for action_key, group_id, level in test_permissions:
            cursor.execute('''
                INSERT OR IGNORE INTO quick_action_permissions 
                (action_key, group_id, permission_level)
                VALUES (?, ?, ?)
            ''', (action_key, group_id, level))
        
        print(f"✅ Permissões adicionadas para grupo Qualidade:")
        print(f"   - Gerar Relatório")
        print(f"   - Gastos por Funcionário")
    
    conn.commit()
    conn.close()

def main():
    """Função principal."""
    test_quick_actions_permissions()
    
    print(f"\n❓ Deseja criar permissões de teste? (s/n): ", end="")
    try:
        response = input().lower().strip()
        if response in ['s', 'sim', 'y', 'yes']:
            create_test_permissions()
            print(f"\n🔄 Executando teste novamente com permissões de exemplo...")
            test_quick_actions_permissions()
    except:
        print(f"\n⏭️ Pulando criação de permissões de teste")

if __name__ == "__main__":
    main()
