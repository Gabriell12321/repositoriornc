#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar os setores disponíveis
"""

import sqlite3
from datetime import datetime, timedelta

def check_sectors():
    """Verificar setores disponíveis"""
    
    print("🔍 Verificando Setores Disponíveis")
    print("="*50)
    
    # Conectar ao banco
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Verificar todos os setores únicos
    cursor.execute("""
        SELECT DISTINCT department, COUNT(*) as count
        FROM rncs 
        WHERE is_deleted = 0 AND department IS NOT NULL AND department != ''
        GROUP BY department
        ORDER BY count DESC
    """)
    
    sectors = cursor.fetchall()
    
    print("📊 Setores Encontrados:")
    for sector, count in sectors:
        print(f"   🏢 {sector}: {count} RNCs")
    
    print()
    
    # Verificar período específico (último mês)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"📅 Período específico: {start_date} a {end_date}")
    
    cursor.execute("""
        SELECT DISTINCT department, COUNT(*) as count
        FROM rncs 
        WHERE is_deleted = 0 
        AND department IS NOT NULL AND department != ''
        AND DATE(created_at) BETWEEN ? AND ?
        GROUP BY department
        ORDER BY count DESC
    """, (start_date, end_date))
    
    sectors_period = cursor.fetchall()
    
    print("📊 Setores no Período:")
    for sector, count in sectors_period:
        print(f"   🏢 {sector}: {count} RNCs")
    
    print()
    
    # Testar a query exata do relatório
    query = """
        SELECT r.*, r.department as creator_department, r.responsavel as creator_name,
               r.department as assigned_department, r.responsavel as assigned_user_name
        FROM rncs r
        WHERE r.is_deleted = 0 
        AND DATE(r.created_at) BETWEEN ? AND ?
        ORDER BY r.department, r.created_at DESC
    """
    
    cursor.execute(query, (start_date, end_date))
    rncs = cursor.fetchall()
    
    # Obter colunas
    columns = [desc[0] for desc in cursor.description]
    rncs_list = [dict(zip(columns, rnc)) for rnc in rncs]
    
    print(f"📊 Total de RNCs na query: {len(rncs_list)}")
    
    # Verificar setores na query
    sectors_in_query = {}
    for rnc in rncs_list:
        sector = rnc['department'] or 'Sem Setor'
        if sector not in sectors_in_query:
            sectors_in_query[sector] = 0
        sectors_in_query[sector] += 1
    
    print("📊 Setores na Query:")
    for sector, count in sectors_in_query.items():
        print(f"   🏢 {sector}: {count} RNCs")
    
    print()
    
    # Verificar se há RNCs sem setor
    cursor.execute("""
        SELECT COUNT(*) 
        FROM rncs 
        WHERE is_deleted = 0 
        AND (department IS NULL OR department = '')
        AND DATE(created_at) BETWEEN ? AND ?
    """, (start_date, end_date))
    
    no_sector = cursor.fetchone()[0]
    print(f"📊 RNCs sem setor: {no_sector}")
    
    conn.close()

if __name__ == "__main__":
    check_sectors()
