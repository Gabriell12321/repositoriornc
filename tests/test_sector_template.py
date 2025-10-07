#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar a lógica do template por setor
"""

import sqlite3
from datetime import datetime, timedelta

def test_sector_template_logic():
    """Testar a lógica do template por setor"""
    
    print("🧪 Testando Lógica do Template por Setor")
    print("="*50)
    
    # Conectar ao banco
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Período de teste (último mês)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"📅 Período: {start_date} a {end_date}")
    print()
    
    # Query exata do relatório
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
    
    print(f"📊 Total de RNCs: {len(rncs_list)}")
    print()
    
    # Simular a lógica do template
    sectors = {}
    
    for rnc in rncs_list:
        sector = rnc['department'] or 'Sem Setor'
        value = float(rnc['price']) if rnc['price'] else 0
        
        # Inicializar setor se não existir
        if sector not in sectors:
            sectors[sector] = {'rncs': [], 'total': 0, 'count': 0}
        
        # Adicionar RNC ao setor
        sectors[sector]['rncs'].append(rnc)
        sectors[sector]['total'] += value
        sectors[sector]['count'] += 1
    
    # Mostrar resultados
    print("📋 Setores Encontrados:")
    for sector_name, sector_data in sectors.items():
        print(f"   🏢 {sector_name}:")
        print(f"      📊 RNCs: {sector_data['count']}")
        print(f"      💰 Valor Total: R$ {sector_data['total']:,.2f}")
        print(f"      📈 Valor Médio: R$ {sector_data['total']/sector_data['count']:,.2f}" if sector_data['count'] > 0 else "      📈 Valor Médio: R$ 0,00")
        
        # Mostrar algumas RNCs do setor
        print(f"      📋 Primeiras 3 RNCs:")
        for i, rnc in enumerate(sector_data['rncs'][:3]):
            value = float(rnc['price']) if rnc['price'] else 0
            print(f"         {i+1}. RNC {rnc['rnc_number']}: R$ {value:,.2f}")
        print()
    
    # Verificar se há problemas nos dados
    print("🔍 Verificação de Dados:")
    
    # Verificar RNCs sem setor
    no_sector = [rnc for rnc in rncs_list if not rnc['department'] or rnc['department'] == '']
    print(f"   📊 RNCs sem setor: {len(no_sector)}")
    
    # Verificar RNCs com setor nulo
    null_sector = [rnc for rnc in rncs_list if rnc['department'] is None]
    print(f"   📊 RNCs com setor NULL: {len(null_sector)}")
    
    # Verificar valores nulos
    null_price = [rnc for rnc in rncs_list if rnc['price'] is None]
    print(f"   📊 RNCs com preço NULL: {len(null_price)}")
    
    # Verificar valores vazios
    empty_price = [rnc for rnc in rncs_list if rnc['price'] == '']
    print(f"   📊 RNCs com preço vazio: {len(empty_price)}")
    
    print()
    
    # Mostrar alguns exemplos de dados
    print("📋 Exemplos de Dados:")
    for i, rnc in enumerate(rncs_list[:5]):
        print(f"   {i+1}. RNC {rnc['rnc_number']}:")
        print(f"      Setor: '{rnc['department']}'")
        print(f"      Preço: '{rnc['price']}'")
        print(f"      Responsável: '{rnc['responsavel']}'")
        print()
    
    conn.close()
    
    print("✅ Teste concluído!")

if __name__ == "__main__":
    test_sector_template_logic()
