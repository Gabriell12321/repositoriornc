#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar os responsáveis reais nos RNCs
"""

import sqlite3
from datetime import datetime, timedelta

def check_real_responsaveis():
    """Verificar responsáveis reais nos RNCs"""
    
    print("🔍 Verificando Responsáveis Reais nos RNCs")
    print("="*50)
    
    # Conectar ao banco
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Período de teste (último mês)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"📅 Período: {start_date} a {end_date}")
    print()
    
    # 1. Verificar todos os valores únicos no campo responsavel
    print("📋 TODOS OS VALORES ÚNICOS NO CAMPO 'responsavel':")
    cursor.execute("""
        SELECT DISTINCT responsavel, COUNT(*) as count
        FROM rncs 
        WHERE is_deleted = 0 
        AND DATE(created_at) BETWEEN ? AND ?
        ORDER BY count DESC
    """, (start_date, end_date))
    
    all_responsaveis = cursor.fetchall()
    
    for responsavel, count in all_responsaveis:
        print(f"   • '{responsavel}': {count} RNCs")
    
    print()
    
    # 2. Verificar RNCs com responsavel = 'None' (string)
    print("⚠️ RNCs COM RESPONSAVEL = 'None' (string):")
    cursor.execute("""
        SELECT rnc_number, title, created_at, price
        FROM rncs 
        WHERE is_deleted = 0 
        AND DATE(created_at) BETWEEN ? AND ?
        AND responsavel = 'None'
        ORDER BY created_at DESC
        LIMIT 10
    """, (start_date, end_date))
    
    rncs_none = cursor.fetchall()
    
    for rnc_number, title, created_at, price in rncs_none:
        print(f"   • RNC {rnc_number}: {title} - {created_at} - R$ {price or 0}")
    
    print()
    
    # 3. Verificar RNCs com responsavel NULL
    print("⚠️ RNCs COM RESPONSAVEL NULL:")
    cursor.execute("""
        SELECT rnc_number, title, created_at, price
        FROM rncs 
        WHERE is_deleted = 0 
        AND DATE(created_at) BETWEEN ? AND ?
        AND responsavel IS NULL
        ORDER BY created_at DESC
        LIMIT 10
    """, (start_date, end_date))
    
    rncs_null = cursor.fetchall()
    
    for rnc_number, title, created_at, price in rncs_null:
        print(f"   • RNC {rnc_number}: {title} - {created_at} - R$ {price or 0}")
    
    print()
    
    # 4. Verificar RNCs com responsavel vazio
    print("⚠️ RNCs COM RESPONSAVEL VAZIO:")
    cursor.execute("""
        SELECT rnc_number, title, created_at, price
        FROM rncs 
        WHERE is_deleted = 0 
        AND DATE(created_at) BETWEEN ? AND ?
        AND responsavel = ''
        ORDER BY created_at DESC
        LIMIT 10
    """, (start_date, end_date))
    
    rncs_empty = cursor.fetchall()
    
    for rnc_number, title, created_at, price in rncs_empty:
        print(f"   • RNC {rnc_number}: {title} - {created_at} - R$ {price or 0}")
    
    print()
    
    # 5. Verificar RNCs com responsavel válido
    print("✅ RNCs COM RESPONSAVEL VÁLIDO:")
    cursor.execute("""
        SELECT responsavel, COUNT(*) as count, SUM(CAST(price AS REAL)) as total_value
        FROM rncs 
        WHERE is_deleted = 0 
        AND DATE(created_at) BETWEEN ? AND ?
        AND responsavel IS NOT NULL 
        AND responsavel != '' 
        AND responsavel != 'None'
        GROUP BY responsavel
        ORDER BY count DESC
    """, (start_date, end_date))
    
    rncs_valid = cursor.fetchall()
    
    for responsavel, count, value in rncs_valid:
        print(f"   • '{responsavel}': {count} RNCs, R$ {value or 0:,.2f}")
    
    print()
    
    # 6. Resumo estatístico
    print("📊 RESUMO ESTATÍSTICO:")
    
    # Total de RNCs no período
    cursor.execute("""
        SELECT COUNT(*) FROM rncs 
        WHERE is_deleted = 0 
        AND DATE(created_at) BETWEEN ? AND ?
    """, (start_date, end_date))
    total_rncs = cursor.fetchone()[0]
    
    # RNCs com responsavel = 'None'
    cursor.execute("""
        SELECT COUNT(*) FROM rncs 
        WHERE is_deleted = 0 
        AND DATE(created_at) BETWEEN ? AND ?
        AND responsavel = 'None'
    """, (start_date, end_date))
    rncs_none_count = cursor.fetchone()[0]
    
    # RNCs com responsavel NULL
    cursor.execute("""
        SELECT COUNT(*) FROM rncs 
        WHERE is_deleted = 0 
        AND DATE(created_at) BETWEEN ? AND ?
        AND responsavel IS NULL
    """, (start_date, end_date))
    rncs_null_count = cursor.fetchone()[0]
    
    # RNCs com responsavel vazio
    cursor.execute("""
        SELECT COUNT(*) FROM rncs 
        WHERE is_deleted = 0 
        AND DATE(created_at) BETWEEN ? AND ?
        AND responsavel = ''
    """, (start_date, end_date))
    rncs_empty_count = cursor.fetchone()[0]
    
    # RNCs com responsavel válido
    cursor.execute("""
        SELECT COUNT(*) FROM rncs 
        WHERE is_deleted = 0 
        AND DATE(created_at) BETWEEN ? AND ?
        AND responsavel IS NOT NULL 
        AND responsavel != '' 
        AND responsavel != 'None'
    """, (start_date, end_date))
    rncs_valid_count = cursor.fetchone()[0]
    
    print(f"   📊 Total de RNCs: {total_rncs}")
    print(f"   ⚠️ Responsável = 'None': {rncs_none_count} ({rncs_none_count/total_rncs*100:.1f}%)")
    print(f"   ⚠️ Responsável = NULL: {rncs_null_count} ({rncs_null_count/total_rncs*100:.1f}%)")
    print(f"   ⚠️ Responsável = '': {rncs_empty_count} ({rncs_empty_count/total_rncs*100:.1f}%)")
    print(f"   ✅ Responsável válido: {rncs_valid_count} ({rncs_valid_count/total_rncs*100:.1f}%)")
    
    print()
    
    # 7. Proposta de solução
    print("🔧 PROPOSTA DE SOLUÇÃO:")
    print("   Como a maioria dos RNCs tem responsável = 'None', vamos:")
    print("   1. Usar o campo 'department' dos RNCs para agrupar por setor")
    print("   2. Mapear os departamentos para os grupos de usuários")
    print("   3. Criar um relatório por grupo baseado no departamento")
    
    print()
    
    # 8. Verificar departamentos dos RNCs
    print("🏢 DEPARTAMENTOS DOS RNCs:")
    cursor.execute("""
        SELECT department, COUNT(*) as count, SUM(CAST(price AS REAL)) as total_value
        FROM rncs 
        WHERE is_deleted = 0 
        AND DATE(created_at) BETWEEN ? AND ?
        AND department IS NOT NULL AND department != ''
        GROUP BY department
        ORDER BY count DESC
    """, (start_date, end_date))
    
    departments = cursor.fetchall()
    
    for dept, count, value in departments:
        print(f"   • {dept}: {count} RNCs, R$ {value or 0:,.2f}")
    
    print()
    
    # 9. Mapeamento departamento → grupo
    print("🗺️ MAPEAMENTO DEPARTAMENTO → GRUPO:")
    mapping = {
        'Engenharia': 'Engenharia',
        'Qualidade': 'Qualidade', 
        'TI': 'TI',
        'Produção': 'Produção',
        'Compras': 'Compras',
        'Administração': 'Administrador',
        'Terceiros': 'Terceiros'
    }
    
    for dept, group in mapping.items():
        print(f"   • {dept} → {group}")
    
    conn.close()
    
    print("\n✅ Análise concluída!")

if __name__ == "__main__":
    check_real_responsaveis()
