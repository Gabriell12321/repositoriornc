#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar estatísticas dos dados atuais
"""

import sqlite3
import os

def get_database_stats():
    """Obter estatísticas do banco de dados"""
    db_path = 'ippel_system.db'
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("📊 ESTATÍSTICAS ATUAIS DO SISTEMA IPPEL")
        print("=" * 60)
        
        # Estatísticas de RNCs
        cursor.execute('SELECT COUNT(*) FROM rncs')
        total_rncs = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM rncs WHERE status = "finalizado"')
        finalizados = cursor.fetchone()[0]
        
        ativos = total_rncs - finalizados
        
        print(f"\n🗂️  RNCs:")
        print(f"   Total: {total_rncs}")
        print(f"   Finalizados: {finalizados}")
        print(f"   Ativos: {ativos}")
        print(f"   % Finalização: {(finalizados/total_rncs*100) if total_rncs > 0 else 0:.1f}%")
        
        # Estatísticas de usuários
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
        active_users = cursor.fetchone()[0]
        
        print(f"\n👥 Usuários:")
        print(f"   Total: {total_users}")
        print(f"   Ativos: {active_users}")
        print(f"   Inativos: {total_users - active_users}")
        
        # Status das RNCs
        cursor.execute('SELECT status, COUNT(*) FROM rncs GROUP BY status ORDER BY COUNT(*) DESC')
        status_results = cursor.fetchall()
        
        print(f"\n📋 RNCs por Status:")
        for status, count in status_results:
            print(f"   {status}: {count}")
        
        # Valores financeiros
        cursor.execute('SELECT SUM(price) FROM rncs')
        total_value = cursor.fetchone()[0] or 0
        
        cursor.execute('SELECT SUM(price) FROM rncs WHERE status = "finalizado"')
        finalized_value = cursor.fetchone()[0] or 0
        
        print(f"\n💰 Valores:")
        print(f"   Total: R$ {total_value:,.2f}")
        print(f"   Finalizados: R$ {finalized_value:,.2f}")
        print(f"   Pendentes: R$ {total_value - finalized_value:,.2f}")
        
        # Últimas atualizações
        cursor.execute('SELECT MAX(created_at) FROM rncs')
        last_rnc = cursor.fetchone()[0]
        
        cursor.execute('SELECT MAX(updated_at) FROM rncs')
        last_update = cursor.fetchone()[0]
        
        print(f"\n⏰ Última Atividade:")
        print(f"   Última RNC criada: {last_rnc or 'N/A'}")
        print(f"   Última atualização: {last_update or 'N/A'}")
        
        # Departamentos
        cursor.execute('SELECT department, COUNT(*) FROM users WHERE department IS NOT NULL AND department != "" GROUP BY department ORDER BY COUNT(*) DESC')
        dept_results = cursor.fetchall()
        
        print(f"\n🏢 Usuários por Departamento:")
        for dept, count in dept_results:
            print(f"   {dept}: {count} usuários")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Análise de estatísticas concluída!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    get_database_stats()