#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para criar sistema de permissões para Ações Rápidas
"""

import sqlite3
import datetime

def create_quick_actions_permissions_table():
    """Cria a tabela para gerenciar permissões das ações rápidas."""
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Criar tabela de ações rápidas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quick_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_key TEXT UNIQUE NOT NULL,
                action_name TEXT NOT NULL,
                action_description TEXT,
                button_html TEXT,
                icon TEXT,
                url TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Criar tabela de permissões das ações rápidas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quick_action_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_key TEXT NOT NULL,
                group_id INTEGER NOT NULL,
                permission_level TEXT DEFAULT 'view',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES groups(id),
                UNIQUE(action_key, group_id)
            )
        ''')
        
        print("✅ Tabelas de permissões criadas com sucesso!")
        
        # Inserir as ações rápidas existentes
        actions = [
            {
                'key': 'manage_users',
                'name': '👥 Gerenciar Usuários',
                'description': 'Acessar o painel de gerenciamento de usuários',
                'icon': '👥',
                'url': '/admin/users'
            },
            {
                'key': 'manage_groups',
                'name': '👥 Gerenciar Grupos',
                'description': 'Acessar o painel de gerenciamento de grupos',
                'icon': '👥',
                'url': '/admin/groups'
            },
            {
                'key': 'manage_permissions',
                'name': '🔐 Gerenciar Permissões',
                'description': 'Acessar o painel de gerenciamento de permissões',
                'icon': '🔐',
                'url': '/admin/permissions'
            },
            {
                'key': 'manage_clients',
                'name': '🏷️ Cadastro de Clientes',
                'description': 'Acessar o cadastro de clientes',
                'icon': '🏷️',
                'url': '/admin/clients'
            },
            {
                'key': 'manage_operators',
                'name': '⏱️ Cadastro de Operador',
                'description': 'Acessar o cadastro de operadores',
                'icon': '⏱️',
                'url': '/admin/operators'
            },
            {
                'key': 'manage_areas',
                'name': '🧭 Cadastro de Área',
                'description': 'Acessar o cadastro de áreas',
                'icon': '🧭',
                'url': '/admin/areas'
            },
            {
                'key': 'generate_report',
                'name': '📊 Gerar Relatório',
                'description': 'Gerar relatórios do sistema',
                'icon': '📊',
                'url': '/reports'
            },
            {
                'key': 'employee_expenses',
                'name': '💰 Gastos por Funcionário',
                'description': 'Visualizar gastos por funcionário',
                'icon': '💰',
                'url': '/reports/employee-expenses'
            }
        ]
        
        for action in actions:
            cursor.execute('''
                INSERT OR IGNORE INTO quick_actions 
                (action_key, action_name, action_description, icon, url)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                action['key'],
                action['name'],
                action['description'],
                action['icon'],
                action['url']
            ))
        
        conn.commit()
        print(f"✅ {len(actions)} ações rápidas inseridas!")
        
        # Mostrar grupos disponíveis
        cursor.execute('SELECT id, name, description FROM groups ORDER BY name')
        groups = cursor.fetchall()
        
        print(f"\n📊 GRUPOS DISPONÍVEIS:")
        for group in groups:
            print(f"  ID: {group[0]}, Nome: {group[1]}, Descrição: {group[2]}")
        
        # Mostrar ações cadastradas
        cursor.execute('SELECT action_key, action_name, action_description FROM quick_actions ORDER BY action_name')
        registered_actions = cursor.fetchall()
        
        print(f"\n⚡ AÇÕES RÁPIDAS CADASTRADAS:")
        for action in registered_actions:
            print(f"  Chave: {action[0]}")
            print(f"  Nome: {action[1]}")
            print(f"  Descrição: {action[2]}")
            
            # Verificar permissões existentes
            cursor.execute('''
                SELECT g.name, qap.permission_level
                FROM quick_action_permissions qap
                JOIN groups g ON qap.group_id = g.id
                WHERE qap.action_key = ?
            ''', (action[0],))
            permissions = cursor.fetchall()
            
            if permissions:
                print(f"  Permissões:")
                for perm in permissions:
                    print(f"    - Grupo: {perm[0]} ({perm[1]})")
            else:
                print(f"  Permissões: Nenhuma (não aparece para ninguém)")
            print()
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erro SQLite: {e}")
        return False

def add_permission_example():
    """Adiciona exemplos de permissões para demonstrar o sistema."""
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        print("\n" + "=" * 70)
        print("ADICIONANDO PERMISSÕES DE EXEMPLO")
        print("=" * 70)
        
        # Exemplo: Dar permissão de "Gerar Relatório" para o grupo TI
        cursor.execute('SELECT id FROM groups WHERE name = "TI"')
        ti_group = cursor.fetchone()
        
        if ti_group:
            cursor.execute('''
                INSERT OR IGNORE INTO quick_action_permissions 
                (action_key, group_id, permission_level)
                VALUES (?, ?, ?)
            ''', ('generate_report', ti_group[0], 'view'))
            
            cursor.execute('''
                INSERT OR IGNORE INTO quick_action_permissions 
                (action_key, group_id, permission_level)
                VALUES (?, ?, ?)
            ''', ('manage_permissions', ti_group[0], 'view'))
            
            print("✅ Permissões adicionadas para grupo TI:")
            print("   - Gerar Relatório")
            print("   - Gerenciar Permissões")
        
        # Exemplo: Dar permissão para grupo Administrador (se existir)
        cursor.execute('SELECT id FROM groups WHERE name = "Administrador"')
        admin_group = cursor.fetchone()
        
        if admin_group:
            # Dar todas as permissões para admin
            cursor.execute('SELECT action_key FROM quick_actions')
            all_actions = cursor.fetchall()
            
            for action in all_actions:
                cursor.execute('''
                    INSERT OR IGNORE INTO quick_action_permissions 
                    (action_key, group_id, permission_level)
                    VALUES (?, ?, ?)
                ''', (action[0], admin_group[0], 'admin'))
            
            print(f"✅ Todas as permissões adicionadas para grupo Administrador")
        
        conn.commit()
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Erro SQLite: {e}")
        return False

def main():
    """Função principal."""
    print("=" * 70)
    print("CRIAÇÃO DO SISTEMA DE PERMISSÕES PARA AÇÕES RÁPIDAS")
    print("=" * 70)
    print("Este sistema permite controlar quais grupos podem ver cada ação rápida.")
    print("Por padrão, nenhuma ação aparece até que seja dada permissão explícita.")
    print("=" * 70)
    
    # Criar estrutura
    if create_quick_actions_permissions_table():
        add_permission_example()
        
        print("\n" + "=" * 70)
        print("✅ SISTEMA DE PERMISSÕES CRIADO COM SUCESSO!")
        print("=" * 70)
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Acessar /admin/quick-actions-permissions para gerenciar permissões")
        print("2. Por padrão, as ações não aparecem para ninguém")
        print("3. Configure as permissões para cada grupo conforme necessário")
        print("\n💡 COMO FUNCIONA:")
        print("- Apenas usuários dos grupos com permissão verão as ações")
        print("- Ações sem permissão não aparecem no dashboard")
        print("- Sistema seguro por padrão (nada aparece sem permissão)")
    else:
        print("\n❌ FALHA AO CRIAR SISTEMA DE PERMISSÕES")

if __name__ == "__main__":
    main()
