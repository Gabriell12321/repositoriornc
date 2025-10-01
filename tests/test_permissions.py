#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys
import os

# Adicionar o caminho do servidor ao sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_department_permissions():
    """Testa as permissões baseadas em departamento"""
    
    # Importar as funções do servidor
    from server_form import get_user_department, has_department_permission, has_permission
    
    # Conectar ao banco
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Buscar alguns usuários de diferentes departamentos
    cursor.execute('''
        SELECT id, name, department, role 
        FROM users 
        WHERE is_active = 1 AND department IS NOT NULL
        LIMIT 10
    ''')
    users = cursor.fetchall()
    conn.close()
    
    print("🔒 TESTE DE PERMISSÕES POR DEPARTAMENTO")
    print("=" * 60)
    
    if not users:
        print("❌ Nenhum usuário encontrado com departamento")
        return
    
    # Definir ações para testar
    actions = [
        'view_own_rncs',
        'view_all_rncs', 
        'view_finalized_rncs',
        'view_charts',
        'view_reports',
        'admin_access',
        'manage_users'
    ]
    
    print(f"{'Usuário':<20} {'Departamento':<15} {'Ação':<20} {'Permissão'}")
    print("-" * 75)
    
    for user in users:
        user_id, name, department, role = user
        print(f"\n👤 {name} ({department})")
        
        for action in actions:
            has_perm = has_department_permission(user_id, action)
            status = "✅ SIM" if has_perm else "❌ NÃO"
            print(f"   {action:<25} {status}")
    
    print("\n" + "=" * 60)
    print("📋 REGRAS APLICADAS:")
    print("• Engenharia: apenas RNCs criadas")
    print("• Produção: apenas RNCs criadas")  
    print("• Qualidade: gráficos, relatórios, RNCs finalizadas e criadas")
    print("• Administração: acesso total")
    print("• TI: acesso total")

if __name__ == '__main__':
    test_department_permissions()
