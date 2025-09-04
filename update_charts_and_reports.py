#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para atualizar automaticamente gráficos e relatórios
Força a atualização dos dados em tempo real
"""

import sqlite3
import json
from datetime import datetime
import os

def update_dashboard_data():
    """Atualizar dados do dashboard em tempo real"""
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    print("🔄 Atualizando dados do dashboard...")
    
    # Estatísticas gerais
    cursor.execute("SELECT COUNT(*) FROM rncs WHERE is_deleted = 0")
    total_rncs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM rncs WHERE status = 'Finalizado' AND is_deleted = 0")
    finalized_rncs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM rncs WHERE status = 'Pendente' AND is_deleted = 0")
    pending_rncs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM rncs WHERE status = 'Em Andamento' AND is_deleted = 0")
    in_progress_rncs = cursor.fetchone()[0]
    
    # Valores totais
    cursor.execute("SELECT SUM(price) FROM rncs WHERE is_deleted = 0")
    total_value = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT SUM(price) FROM rncs WHERE status = 'Finalizado' AND is_deleted = 0")
    finalized_value = cursor.fetchone()[0] or 0
    
    # Por departamento
    cursor.execute("""
        SELECT department, COUNT(*), SUM(price)
        FROM rncs 
        WHERE is_deleted = 0 
        GROUP BY department
        ORDER BY COUNT(*) DESC
    """)
    dept_stats = cursor.fetchall()
    
    # Por status
    cursor.execute("""
        SELECT status, COUNT(*), SUM(price)
        FROM rncs 
        WHERE is_deleted = 0 
        GROUP BY status
        ORDER BY COUNT(*) DESC
    """)
    status_stats = cursor.fetchall()
    
    # Por mês (últimos 12 meses)
    cursor.execute("""
        SELECT strftime('%Y-%m', created_at) as month, COUNT(*), SUM(price)
        FROM rncs 
        WHERE is_deleted = 0 
        AND created_at >= date('now', '-12 months')
        GROUP BY month
        ORDER BY month DESC
    """)
    monthly_stats = cursor.fetchall()
    
    # Criar arquivo de dados atualizados
    dashboard_data = {
        'last_updated': datetime.now().isoformat(),
        'summary': {
            'total_rncs': total_rncs,
            'finalized_rncs': finalized_rncs,
            'pending_rncs': pending_rncs,
            'in_progress_rncs': in_progress_rncs,
            'total_value': float(total_value),
            'finalized_value': float(finalized_value)
        },
        'by_department': [
            {
                'department': dept,
                'count': count,
                'value': float(value or 0)
            } for dept, count, value in dept_stats
        ],
        'by_status': [
            {
                'status': status,
                'count': count,
                'value': float(value or 0)
            } for status, count, value in status_stats
        ],
        'by_month': [
            {
                'month': month,
                'count': count,
                'value': float(value or 0)
            } for month, count, value in monthly_stats
        ]
    }
    
    # Salvar dados atualizados
    with open('static/dashboard_data.json', 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Dashboard atualizado:")
    print(f"   📊 Total RNCs: {total_rncs}")
    print(f"   ✅ Finalizadas: {finalized_rncs}")
    print(f"   ⏳ Pendentes: {pending_rncs}")
    print(f"   🔄 Em Andamento: {in_progress_rncs}")
    print(f"   💰 Valor Total: R$ {total_value:,.2f}")
    print(f"   💰 Valor Finalizado: R$ {finalized_value:,.2f}")
    
    conn.close()

def update_report_cache():
    """Limpar cache dos relatórios para forçar atualização"""
    
    print("🔄 Limpando cache dos relatórios...")
    
    # Lista de arquivos de cache que podem existir
    cache_files = [
        'static/cache/finalized_rncs.json',
        'static/cache/total_detailed.json',
        'static/cache/by_operator.json',
        'static/cache/by_sector.json'
    ]
    
    for cache_file in cache_files:
        if os.path.exists(cache_file):
            os.remove(cache_file)
            print(f"   🗑️ Removido: {cache_file}")
    
    print("✅ Cache limpo!")

def force_template_reload():
    """Forçar recarregamento dos templates"""
    
    print("🔄 Forçando recarregamento dos templates...")
    
    # Criar arquivo de timestamp para forçar atualização
    timestamp_file = 'static/last_update.txt'
    with open(timestamp_file, 'w') as f:
        f.write(datetime.now().isoformat())
    
    print("✅ Templates marcados para recarregamento!")

def main():
    """Função principal"""
    
    print("🚀 Iniciando atualização automática de gráficos e relatórios...")
    print("="*60)
    
    try:
        # 1. Atualizar dados do dashboard
        update_dashboard_data()
        print()
        
        # 2. Limpar cache dos relatórios
        update_report_cache()
        print()
        
        # 3. Forçar recarregamento dos templates
        force_template_reload()
        print()
        
        print("="*60)
        print("✅ Atualização completa!")
        print("📊 Os gráficos e relatórios agora refletem os dados mais recentes")
        print("🔄 Para atualização automática, execute este script periodicamente")
        
    except Exception as e:
        print(f"❌ Erro durante a atualização: {e}")

if __name__ == "__main__":
    main()
