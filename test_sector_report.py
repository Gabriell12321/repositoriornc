#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o relatório por setor
"""

import sqlite3
from datetime import datetime, timedelta

def test_sector_report():
    """Testar o relatório por setor"""
    
    print("🧪 Testando Relatório por Setor")
    print("="*50)
    
    # Conectar ao banco
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Definir período de teste (último mês)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"📅 Período de teste: {start_date} a {end_date}")
    print()
    
    # Testar query do relatório por setor
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
    
    print(f"📊 Total de RNCs encontradas: {len(rncs_list)}")
    print()
    
    # Organizar por setor
    sectors = {}
    
    for rnc in rncs_list:
        sector = rnc['department'] or 'Sem Setor'
        value = float(rnc['price']) if rnc['price'] else 0
        
        if sector not in sectors:
            sectors[sector] = {'rncs': [], 'total': 0, 'count': 0}
        
        sectors[sector]['rncs'].append(rnc)
        sectors[sector]['total'] += value
        sectors[sector]['count'] += 1
    
    # Mostrar resultados
    print("📋 Resumo por Setor:")
    for sector_name, sector_data in sectors.items():
        print(f"   🏢 {sector_name}:")
        print(f"      📊 RNCs: {sector_data['count']}")
        print(f"      💰 Valor Total: R$ {sector_data['total']:,.2f}")
        print(f"      📈 Valor Médio: R$ {sector_data['total']/sector_data['count']:,.2f}" if sector_data['count'] > 0 else "      📈 Valor Médio: R$ 0,00")
        
        # Mostrar top 3 RNCs do setor
        sorted_rncs = sorted(sector_data['rncs'], key=lambda x: float(x['price']) if x['price'] else 0, reverse=True)
        print(f"      🏆 Top 3 RNCs:")
        for i, rnc in enumerate(sorted_rncs[:3]):
            value = float(rnc['price']) if rnc['price'] else 0
            print(f"         {i+1}. RNC {rnc['rnc_number']}: R$ {value:,.2f} - {rnc['responsavel'] or 'Sem responsável'}")
        print()
    
    # Testar estatísticas
    print("📈 Estatísticas Gerais:")
    
    # Total de RNCs no período
    cursor.execute("""
        SELECT COUNT(*) FROM rncs 
        WHERE is_deleted = 0 AND DATE(created_at) BETWEEN ? AND ?
    """, (start_date, end_date))
    total_rncs = cursor.fetchone()[0]
    print(f"   📊 Total de RNCs: {total_rncs}")
    
    # RNCs por setor
    cursor.execute("""
        SELECT r.department, COUNT(*) FROM rncs r
        WHERE r.is_deleted = 0 AND DATE(r.created_at) BETWEEN ? AND ?
        GROUP BY r.department
        ORDER BY COUNT(*) DESC
    """, (start_date, end_date))
    by_sector = dict(cursor.fetchall())
    print(f"   🏢 RNCs por Setor: {by_sector}")
    
    # Valor por setor
    cursor.execute("""
        SELECT r.department, SUM(CAST(r.price AS REAL)) FROM rncs r
        WHERE r.is_deleted = 0 AND DATE(r.created_at) BETWEEN ? AND ?
        AND r.price IS NOT NULL AND r.price != ''
        GROUP BY r.department
        ORDER BY SUM(CAST(r.price AS REAL)) DESC
    """, (start_date, end_date))
    value_by_sector = dict(cursor.fetchall())
    print(f"   💰 Valor por Setor: {value_by_sector}")
    
    conn.close()
    
    print()
    print("✅ Teste concluído!")
    print("🌐 Para testar o relatório: http://172.26.0.75:5001/reports/menu")
    print("📋 Selecione 'Por Setor' e escolha o período")

if __name__ == "__main__":
    test_sector_report()
