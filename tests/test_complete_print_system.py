#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final da funcionalidade de impressão de relatórios com permissões
"""

import sqlite3
import sys
import os

# Adicionar o caminho do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from services.permissions import has_permission
    from services.db import DB_PATH
except ImportError:
    print("⚠️ Módulos de serviços não encontrados - executando verificação básica")
    has_permission = None
    DB_PATH = 'ippel_system.db'

def test_permission_system():
    """Testa o sistema de permissões"""
    print("🔐 TESTE DO SISTEMA DE PERMISSÕES")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar usuários que têm a permissão
        cursor.execute("""
            SELECT u.id, u.name, u.email, u.role, g.name as group_name,
                   COALESCE(gp.permission_value, 0) as can_print
            FROM users u
            LEFT JOIN groups g ON u.group_id = g.id
            LEFT JOIN group_permissions gp ON g.id = gp.group_id 
                AND gp.permission_name = 'can_print_reports'
            ORDER BY u.name
        """)
        
        users = cursor.fetchall()
        
        print("👥 USUÁRIOS E SUAS PERMISSÕES DE IMPRESSÃO:")
        print("-" * 60)
        for user in users:
            user_id, name, email, role, group_name, can_print = user
            status = "✅ PERMITIDO" if can_print else "❌ NEGADO"
            print(f"• {name} ({email})")
            print(f"  Grupo: {group_name or 'Sem grupo'} | Role: {role}")
            print(f"  Permissão: {status}")
            print()
        
        # Verificar se há usuários administradores
        admin_users = [u for u in users if u[5] == 1]  # can_print = 1
        if admin_users:
            print(f"✅ {len(admin_users)} usuário(s) com permissão de impressão")
            print("📝 Usuários que podem ver o botão 'Imprimir Relatório':")
            for user in admin_users:
                print(f"   • {user[1]} ({user[4]})")
        else:
            print("⚠️ Nenhum usuário tem permissão de impressão habilitada")
            print("💡 Use: python configure_print_permissions.py --enable GROUP_ID")
        
        conn.close()
        return len(admin_users) > 0
        
    except Exception as e:
        print(f"❌ Erro ao testar permissões: {e}")
        return False

def test_files_structure():
    """Testa se todos os arquivos necessários existem"""
    print("\n📁 TESTE DA ESTRUTURA DE ARQUIVOS")
    print("=" * 50)
    
    required_files = [
        'routes/print_reports.py',
        'templates/reports/print_detailed.html',
        'templates/reports/print_summary.html',
        'templates/reports/print_charts.html',
        'templates/dashboard_improved.html'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - AUSENTE!")
            all_exist = False
    
    return all_exist

def test_dashboard_integration():
    """Testa se o dashboard tem a integração correta"""
    print("\n🎛️ TESTE DA INTEGRAÇÃO DO DASHBOARD")
    print("=" * 50)
    
    try:
        with open('templates/dashboard_improved.html', 'r', encoding='utf-8') as f:
            dashboard_content = f.read()
        
        checks = [
            ('canPrintReports', 'Verificação de permissão no template'),
            ('showPrintReportModal', 'Função JavaScript do modal'),
            ('🖨️ Imprimir Relatório', 'Texto do botão'),
            ('printReportModal', 'ID do modal'),
        ]
        
        all_passed = True
        for check_text, description in checks:
            if check_text in dashboard_content:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} - NÃO ENCONTRADO!")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Erro ao verificar dashboard: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🧪 TESTE COMPLETO - IMPRESSÃO DE RELATÓRIOS COM PERMISSÕES")
    print("=" * 70)
    
    # Executar todos os testes
    test_results = [
        test_files_structure(),
        test_dashboard_integration(),
        test_permission_system()
    ]
    
    # Resultado final
    print("\n" + "=" * 70)
    if all(test_results):
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema de impressão de relatórios implementado e configurado")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Reiniciar o servidor Flask")
        print("2. Fazer login com usuário que tem permissão")
        print("3. Verificar se o botão 'Imprimir Relatório' aparece nas Ações Rápidas")
        print("4. Testar a funcionalidade")
        print("\n🎯 PARA HABILITAR MAIS GRUPOS:")
        print("python configure_print_permissions.py --enable GROUP_ID")
        print("Exemplo: python configure_print_permissions.py --enable 2  # Qualidade")
    else:
        failed_tests = ["Estrutura de arquivos", "Integração dashboard", "Sistema de permissões"]
        failed = [test for i, test in enumerate(failed_tests) if not test_results[i]]
        print("❌ ALGUNS TESTES FALHARAM:")
        for test in failed:
            print(f"   • {test}")
        print("\n⚠️ Corrija os problemas antes de usar o sistema")

if __name__ == "__main__":
    main()
