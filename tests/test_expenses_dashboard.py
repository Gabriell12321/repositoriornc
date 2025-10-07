#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o novo painel de gastos por funcionário
"""

import sqlite3
from datetime import datetime

def test_expenses_dashboard():
    """Testar o novo painel de gastos por funcionário"""
    
    print("🧪 Testando Painel de Gastos por Funcionário")
    print("="*50)
    
    # Conectar ao banco
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Estatísticas gerais
    cursor.execute("SELECT COUNT(*) FROM rncs WHERE is_deleted = 0")
    total_rncs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM rncs WHERE status = 'Finalizado' AND is_deleted = 0")
    finalized_rncs = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(price) FROM rncs WHERE is_deleted = 0")
    total_value = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(price) FROM rncs WHERE status = 'Finalizado' AND is_deleted = 0")
    finalized_value = cursor.fetchone()[0] or 0
    
    print(f"📊 Estatísticas Gerais:")
    print(f"   Total de RNCs: {total_rncs}")
    print(f"   RNCs Finalizadas: {finalized_rncs}")
    print(f"   Valor Total: R$ {total_value:,.2f}")
    print(f"   Valor Finalizado: R$ {finalized_value:,.2f}")
    print()
    
    # Organizar dados por departamento e responsável
    cursor.execute("""
        SELECT department, responsavel, SUM(price) as total_value, COUNT(*) as rnc_count
        FROM rncs 
        WHERE is_deleted = 0 AND responsavel IS NOT NULL AND responsavel != ''
        GROUP BY department, responsavel
        ORDER BY department, total_value DESC
    """)
    
    dept_employee_data = cursor.fetchall()
    
    print(f"👥 Dados por Departamento e Responsável:")
    print(f"   Total de registros: {len(dept_employee_data)}")
    print()
    
    # Organizar em estrutura hierárquica
    departments = {}
    
    for dept, responsavel, value, count in dept_employee_data:
        if dept not in departments:
            departments[dept] = {'employees': {}, 'total': 0}
        
        # Usar o responsável diretamente
        employee_name = responsavel if responsavel else "Sistema"
        
        departments[dept]['employees'][employee_name] = value
        departments[dept]['total'] += value
    
    # Mostrar resultados
    print("📋 Resumo por Departamento:")
    for dept_name, dept_data in departments.items():
        print(f"   🏢 {dept_name}: R$ {dept_data['total']:,.2f}")
        print(f"      👥 Funcionários: {len(dept_data['employees'])}")
        
        # Mostrar top 3 funcionários
        sorted_employees = sorted(dept_data['employees'].items(), key=lambda x: x[1], reverse=True)
        for i, (emp_name, emp_value) in enumerate(sorted_employees[:3]):
            print(f"      {i+1}. {emp_name}: R$ {emp_value:,.2f}")
        print()
    
    conn.close()
    
    print("✅ Teste concluído!")
    print("🌐 Para acessar o painel: http://localhost:5000/dashboard/expenses")
    print("🔗 Botão disponível no dashboard principal: '💰 Gastos por Funcionário'")

if __name__ == "__main__":
    test_expenses_dashboard()
