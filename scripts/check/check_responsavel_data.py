#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar dados de responsável
"""

import sqlite3

def check_responsavel_data():
    """Verificar dados de responsável no banco"""
    
    print("🔍 Verificando dados de responsável...")
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Verificar se a coluna existe
    cursor.execute("PRAGMA table_info(rncs)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'responsavel' not in columns:
        print("❌ Coluna 'responsavel' não encontrada!")
        return
    
    print("✅ Coluna 'responsavel' encontrada!")
    
    # Verificar quantas RNCs têm responsável
    cursor.execute("SELECT COUNT(*) FROM rncs WHERE responsavel IS NOT NULL AND responsavel != ''")
    with_responsavel = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM rncs")
    total = cursor.fetchone()[0]
    
    print(f"📊 RNCs com responsável: {with_responsavel}/{total} ({with_responsavel/total*100:.1f}%)")
    
    # Verificar responsáveis únicos
    cursor.execute("""
        SELECT responsavel, COUNT(*) as count, SUM(price) as total_value
        FROM rncs 
        WHERE responsavel IS NOT NULL AND responsavel != ''
        GROUP BY responsavel
        ORDER BY total_value DESC
        LIMIT 10
    """)
    
    results = cursor.fetchall()
    
    print("\n📋 Top 10 Responsáveis por Valor:")
    for responsavel, count, value in results:
        print(f"   👤 {responsavel}: {count} RNCs, R$ {value:,.2f}")
    
    # Verificar por departamento
    cursor.execute("""
        SELECT department, responsavel, COUNT(*) as count, SUM(price) as total_value
        FROM rncs 
        WHERE responsavel IS NOT NULL AND responsavel != ''
        GROUP BY department, responsavel
        ORDER BY department, total_value DESC
        LIMIT 20
    """)
    
    dept_results = cursor.fetchall()
    
    print("\n📋 Responsáveis por Departamento:")
    current_dept = None
    for dept, responsavel, count, value in dept_results:
        if dept != current_dept:
            print(f"\n🏢 {dept}:")
            current_dept = dept
        print(f"   👤 {responsavel}: {count} RNCs, R$ {value:,.2f}")
    
    conn.close()

if __name__ == "__main__":
    check_responsavel_data()
