#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para testar a API de desempenho e identificar o problema
"""

import sqlite3
import json

# Configurações
DB_PATH = "ippel_system.db"

def test_direct_query():
    """Testa a query diretamente no banco"""
    print("🔍 Testando query diretamente no banco...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Query exata da API
        query = """
            SELECT 
                r.user_id as owner_id,
                COUNT(r.id) as rnc_count
            FROM rncs r
            WHERE r.status IN ('Finalizado','finalized')
              AND r.is_deleted = 0
              AND r.user_id IS NOT NULL
            GROUP BY owner_id
            ORDER BY rnc_count DESC
        """
        
        print(f"🔍 Executando query: {query}")
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"📊 Resultados da query:")
        for user_id, count in results:
            print(f"   Usuário ID {user_id}: {count} RNCs")
        
        # Verificar usuários
        cursor.execute("""
            SELECT id, name, department FROM users 
            WHERE name IS NOT NULL 
              AND name != '' 
              AND (is_active = 1 OR is_active IS NULL)
            ORDER BY name
        """)
        users = cursor.fetchall()
        
        print(f"\n👥 Usuários encontrados: {len(users)}")
        for user_id, name, dept in users[:10]:
            print(f"   ID {user_id}: {name} - {dept or 'Sem departamento'}")
        
        # Simular o processamento da API
        rnc_data = {row[0]: row[1] for row in results}
        print(f"\n📊 Dados de RNCs processados: {rnc_data}")
        
        meta_mensal = 5
        result = []
        for user_id, user_name, department in users:
            rncs = rnc_data.get(user_id, 0)
            percentage = (rncs / meta_mensal * 100) if meta_mensal > 0 else 0
            status = 'Acima da Meta' if rncs >= meta_mensal else 'Abaixo da Meta'
            result.append({
                'name': user_name,
                'rncs': rncs,
                'meta': meta_mensal,
                'percentage': round(percentage, 1),
                'status': status,
                'department': department or 'Não definido'
            })
        
        result.sort(key=lambda x: x['percentage'], reverse=True)
        print(f"\n✅ Resultado final simulado:")
        for emp in result[:5]:
            print(f"   👤 {emp['name']}: {emp['rncs']} RNCs ({emp['percentage']}%) - {emp['status']}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro no teste direto: {e}")
        import traceback
        traceback.print_exc()

def test_with_filters():
    """Testa a query com filtros de ano e mês"""
    print("\n🗓️ Testando query com filtros...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Testar com filtro de ano 2025
        query_2025 = """
            SELECT 
                r.user_id as owner_id,
                COUNT(r.id) as rnc_count
            FROM rncs r
            WHERE r.status IN ('Finalizado','finalized')
              AND r.is_deleted = 0
              AND r.user_id IS NOT NULL
              AND strftime('%Y', r.created_at) = '2025'
            GROUP BY owner_id
            ORDER BY rnc_count DESC
        """
        
        print(f"🔍 Query com filtro ano 2025:")
        cursor.execute(query_2025)
        results_2025 = cursor.fetchall()
        
        print(f"📊 Resultados 2025:")
        for user_id, count in results_2025:
            print(f"   Usuário ID {user_id}: {count} RNCs")
        
        # Testar com filtro de mês 12/2025
        query_dec_2025 = """
            SELECT 
                r.user_id as owner_id,
                COUNT(r.id) as rnc_count
            FROM rncs r
            WHERE r.status IN ('Finalizado','finalized')
              AND r.is_deleted = 0
              AND r.user_id IS NOT NULL
              AND strftime('%Y', r.created_at) = '2025'
              AND strftime('%m', r.created_at) = '12'
            GROUP BY owner_id
            ORDER BY rnc_count DESC
        """
        
        print(f"\n🔍 Query com filtro dezembro 2025:")
        cursor.execute(query_dec_2025)
        results_dec_2025 = cursor.fetchall()
        
        print(f"📊 Resultados dezembro 2025:")
        for user_id, count in results_dec_2025:
            print(f"   Usuário ID {user_id}: {count} RNCs")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro no teste com filtros: {e}")
        import traceback
        traceback.print_exc()

def check_date_format():
    """Verifica o formato das datas no banco"""
    print("\n📅 Verificando formato das datas...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar algumas datas
        cursor.execute("""
            SELECT id, created_at, finalized_at
            FROM rncs 
            WHERE is_deleted = 0
            ORDER BY created_at DESC
            LIMIT 10
        """)
        dates = cursor.fetchall()
        
        print(f"📅 Últimas 10 datas de criação:")
        for rnc_id, created, finalized in dates:
            print(f"   RNC {rnc_id}: Criada: {created} | Finalizada: {finalized}")
        
        # Verificar se há datas em formato diferente
        cursor.execute("""
            SELECT DISTINCT strftime('%Y', created_at) as year
            FROM rncs 
            WHERE created_at IS NOT NULL AND is_deleted = 0
            ORDER BY year DESC
        """)
        years = cursor.fetchall()
        
        print(f"\n📅 Anos encontrados: {[row[0] for row in years if row[0]]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar datas: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Função principal"""
    print("🚀 Iniciando teste da API de desempenho...")
    
    # Testar query direta
    test_direct_query()
    
    # Testar com filtros
    test_with_filters()
    
    # Verificar formato das datas
    check_date_format()
    
    print("\n✨ Teste concluído!")

if __name__ == "__main__":
    main()
