#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o relatório por grupo
"""

import sqlite3
from datetime import datetime, timedelta

def test_group_report():
    """Testar relatório por grupo"""
    
    print("🧪 Testando Relatório por Grupo")
    print("="*50)
    
    # Conectar ao banco
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Período de teste (último mês)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"📅 Período: {start_date} a {end_date}")
    print()
    
    # Query do relatório por grupo
    query = """
        SELECT r.*, r.department as creator_department, r.responsavel as creator_name,
               r.department as assigned_department, r.responsavel as assigned_user_name,
               CASE 
                   WHEN r.department = 'Engenharia' THEN 'Engenharia'
                   WHEN r.department = 'Qualidade' THEN 'Qualidade'
                   WHEN r.department = 'TI' THEN 'TI'
                   WHEN r.department = 'Produção' THEN 'Produção'
                   WHEN r.department = 'Compras' THEN 'Compras'
                   WHEN r.department = 'Administração' THEN 'Administrador'
                   WHEN r.department = 'Terceiros' THEN 'Terceiros'
                   ELSE 'Outros'
               END as group_name
        FROM rncs r
        WHERE r.is_deleted = 0 
        AND DATE(r.created_at) BETWEEN ? AND ?
        ORDER BY group_name, r.department, r.created_at DESC
    """
    
    cursor.execute(query, (start_date, end_date))
    rncs = cursor.fetchall()
    
    # Obter colunas
    columns = [desc[0] for desc in cursor.description]
    rncs_list = [dict(zip(columns, rnc)) for rnc in rncs]
    
    print(f"📊 Total de RNCs: {len(rncs_list)}")
    print()
    
    # Simular a lógica do template
    groups = {}
    
    for rnc in rncs_list:
        group = rnc['group_name'] or 'Sem Grupo'
        value = float(rnc['price']) if rnc['price'] else 0
        
        # Inicializar grupo se não existir
        if group not in groups:
            groups[group] = {'rncs': [], 'total': 0, 'count': 0}
        
        # Adicionar RNC ao grupo
        groups[group]['rncs'].append(rnc)
        groups[group]['total'] += value
        groups[group]['count'] += 1
    
    # Mostrar resultados
    print("📋 Grupos Encontrados:")
    for group_name, group_data in groups.items():
        print(f"   🏢 {group_name}:")
        print(f"      📊 RNCs: {group_data['count']}")
        print(f"      💰 Valor Total: R$ {group_data['total']:,.2f}")
        print(f"      📈 Valor Médio: R$ {group_data['total']/group_data['count']:,.2f}" if group_data['count'] > 0 else "      📈 Valor Médio: R$ 0,00")
        
        # Mostrar departamentos neste grupo
        departments = {}
        for rnc in group_data['rncs']:
            dept = rnc['department'] or 'Sem Departamento'
            if dept not in departments:
                departments[dept] = 0
            departments[dept] += 1
        
        print(f"      📋 Departamentos: {', '.join([f'{dept} ({count})' for dept, count in departments.items()])}")
        
        # Mostrar algumas RNCs do grupo
        print(f"      📋 Primeiras 3 RNCs:")
        for i, rnc in enumerate(group_data['rncs'][:3]):
            value = float(rnc['price']) if rnc['price'] else 0
            print(f"         {i+1}. RNC {rnc['rnc_number']}: R$ {value:,.2f} ({rnc['department']})")
        print()
    
    # Verificar mapeamento departamento → grupo
    print("🗺️ MAPEAMENTO DEPARTAMENTO → GRUPO:")
    dept_group_mapping = {}
    
    for rnc in rncs_list:
        dept = rnc['department']
        group = rnc['group_name']
        if dept not in dept_group_mapping:
            dept_group_mapping[dept] = group
    
    for dept, group in dept_group_mapping.items():
        print(f"   • {dept} → {group}")
    
    print()
    
    # Verificar se há departamentos não mapeados
    print("🔍 VERIFICAÇÃO DE DEPARTAMENTOS:")
    all_departments = set(rnc['department'] for rnc in rncs_list if rnc['department'])
    mapped_departments = set(dept_group_mapping.keys())
    
    print(f"   📊 Total de departamentos: {len(all_departments)}")
    print(f"   ✅ Departamentos mapeados: {len(mapped_departments)}")
    
    if all_departments != mapped_departments:
        unmapped = all_departments - mapped_departments
        print(f"   ⚠️ Departamentos não mapeados: {unmapped}")
    
    print()
    
    # Estatísticas finais
    print("📊 ESTATÍSTICAS FINAIS:")
    total_rncs = len(rncs_list)
    total_value = sum(float(rnc['price']) if rnc['price'] else 0 for rnc in rncs_list)
    
    print(f"   📊 Total de RNCs: {total_rncs}")
    print(f"   💰 Valor Total: R$ {total_value:,.2f}")
    print(f"   🏢 Grupos: {len(groups)}")
    print(f"   📋 Departamentos: {len(all_departments)}")
    
    conn.close()
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    test_group_report()
