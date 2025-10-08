#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar a API de indicadores por setor
"""
import sqlite3

def test_setor_api(setor_key):
    # Mapeamento de setor para nome no banco
    setor_mapping = {
        'engenharia': 'Engenharia',
        'producao': 'Produção',
        'pcp': 'PCP',
        'qualidade': 'Qualidade',
        'compras': 'Compras',
        'comercial': 'Comercial',
        'terceiros': 'Terceiros',
        'expedicao': 'Expedição',
        'almoxarifado': 'Almoxarifado'
    }
    
    setor_nome = setor_mapping.get(setor_key.lower())
    if not setor_nome:
        print(f"❌ Setor '{setor_key}' não encontrado no mapeamento")
        return
    
    print(f"\n{'='*80}")
    print(f"🔍 Testando API para setor: {setor_key} → {setor_nome}")
    print(f"{'='*80}\n")
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Buscar RNCs do setor
    cursor.execute("""
        SELECT 
            id, rnc_number, title, area_responsavel, setor, 
            status, finalized_at, created_at, price
        FROM rncs 
        WHERE (
            LOWER(TRIM(area_responsavel)) LIKE ?
            OR LOWER(TRIM(setor)) LIKE ?
        )
        AND (is_deleted = 0 OR is_deleted IS NULL)
        ORDER BY COALESCE(finalized_at, created_at) DESC
        LIMIT 10
    """, (f'%{setor_nome.lower()}%', f'%{setor_nome.lower()}%'))
    
    rncs = cursor.fetchall()
    
    print(f"📊 Total de RNCs encontradas: {len(rncs)}")
    
    if rncs:
        print(f"\n📋 Primeiras 10 RNCs:")
        print(f"{'-'*100}")
        print(f"{'ID':<8} {'RNC':<10} {'Título':<30} {'Área':<15} {'Setor':<15} {'Status':<12}")
        print(f"{'-'*100}")
        
        for rnc in rncs:
            id_, rnc_num, title, area, setor, status = rnc[0:6]
            title_short = (title[:27] + '...') if len(title) > 30 else title
            area_short = (area[:12] + '...') if area and len(area) > 15 else (area or '-')
            setor_short = (setor[:12] + '...') if setor and len(setor) > 15 else (setor or '-')
            
            print(f"{id_:<8} {rnc_num:<10} {title_short:<30} {area_short:<15} {setor_short:<15} {status:<12}")
    
    # Estatísticas mensais
    print(f"\n📈 RNCs por Mês/Ano:")
    print(f"{'-'*60}")
    
    cursor.execute("""
        SELECT 
            strftime('%Y-%m', COALESCE(finalized_at, created_at)) as mes_ano,
            COUNT(*) as total,
            SUM(CAST(COALESCE(price, 0) AS REAL)) as valor_total
        FROM rncs 
        WHERE (
            LOWER(TRIM(area_responsavel)) LIKE ?
            OR LOWER(TRIM(setor)) LIKE ?
        )
        AND (is_deleted = 0 OR is_deleted IS NULL)
        AND COALESCE(finalized_at, created_at) IS NOT NULL
        GROUP BY mes_ano
        ORDER BY mes_ano DESC
        LIMIT 24
    """, (f'%{setor_nome.lower()}%', f'%{setor_nome.lower()}%'))
    
    monthly = cursor.fetchall()
    
    if monthly:
        print(f"{'Mês/Ano':<15} {'Quantidade':<15} {'Valor Total':<20}")
        print(f"{'-'*60}")
        
        total_rncs = 0
        total_valor = 0.0
        
        for mes, qtd, valor in reversed(monthly):  # Ordem crescente
            total_rncs += qtd
            total_valor += (valor or 0)
            print(f"{mes:<15} {qtd:<15} R$ {valor or 0:>15,.2f}")
        
        print(f"{'-'*60}")
        print(f"{'TOTAL':<15} {total_rncs:<15} R$ {total_valor:>15,.2f}")
    else:
        print("❌ Nenhum dado mensal encontrado")
    
    # Verificar campos críticos
    print(f"\n🔍 Análise de Campos:")
    print(f"{'-'*60}")
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN area_responsavel IS NOT NULL AND area_responsavel != '' THEN 1 END) as com_area,
            COUNT(CASE WHEN setor IS NOT NULL AND setor != '' THEN 1 END) as com_setor,
            COUNT(CASE WHEN finalized_at IS NOT NULL THEN 1 END) as com_finalized,
            COUNT(CASE WHEN status = 'Finalizado' THEN 1 END) as status_finalizado
        FROM rncs 
        WHERE (
            LOWER(TRIM(area_responsavel)) LIKE ?
            OR LOWER(TRIM(setor)) LIKE ?
        )
        AND (is_deleted = 0 OR is_deleted IS NULL)
    """, (f'%{setor_nome.lower()}%', f'%{setor_nome.lower()}%'))
    
    stats = cursor.fetchone()
    total, com_area, com_setor, com_finalized, status_finalizado = stats
    
    print(f"Total RNCs: {total}")
    print(f"Com área_responsavel: {com_area} ({com_area/total*100:.1f}%)")
    print(f"Com setor: {com_setor} ({com_setor/total*100:.1f}%)")
    print(f"Com finalized_at: {com_finalized} ({com_finalized/total*100:.1f}%)")
    print(f"Status 'Finalizado': {status_finalizado} ({status_finalizado/total*100:.1f}%)")
    
    conn.close()
    
    print(f"\n{'='*80}\n")

if __name__ == '__main__':
    # Testar todos os setores principais
    setores = ['engenharia', 'producao', 'pcp', 'qualidade', 'expedicao', 
               'almoxarifado', 'compras', 'comercial', 'terceiros']
    
    for setor in setores:
        test_setor_api(setor)
