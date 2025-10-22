#!/usr/bin/env python3
"""
Script para testar a API de indicadores por setor
"""
import sqlite3
import json
from datetime import datetime

def test_database_connection():
    """Testa a conexão com o banco de dados"""
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Verificar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("Tabelas encontradas:", [table[0] for table in tables])
        
        # Verificar se existe a tabela rncs
        cursor.execute("SELECT COUNT(*) FROM rncs WHERE is_deleted = 0 OR is_deleted IS NULL")
        total_rncs = cursor.fetchone()[0]
        print(f"Total de RNCs: {total_rncs}")
        
        # Verificar setores disponíveis
        cursor.execute("""
            SELECT DISTINCT area_responsavel, setor, COUNT(*) as count
            FROM rncs 
            WHERE (is_deleted = 0 OR is_deleted IS NULL)
            GROUP BY area_responsavel, setor
            ORDER BY count DESC
            LIMIT 10
        """)
        setores = cursor.fetchall()
        print("Setores encontrados:")
        for setor in setores:
            print(f"  {setor[0]} | {setor[1]} | {setor[2]} RNCs")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erro ao conectar com o banco: {e}")
        return False

def test_setor_data(setor='engenharia'):
    """Testa os dados de um setor específico"""
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Mapeamento de setor
        setor_mapping = {
            'engenharia': 'Engenharia',
            'producao': 'Produção',
            'pcp': 'PCP',
            'qualidade': 'Qualidade',
            'compras': 'Compras',
            'comercial': 'Comercial',
            'terceiros': 'Terceiros'
        }
        
        setor_nome = setor_mapping.get(setor, setor)
        print(f"\nTestando setor: {setor} -> {setor_nome}")
        
        # Buscar RNCs do setor
        cursor.execute("""
            SELECT 
                id, rnc_number, title, client, equipment, area_responsavel,
                setor, status, priority, finalized_at, created_at, price
            FROM rncs 
            WHERE (
                LOWER(TRIM(area_responsavel)) LIKE ?
                OR LOWER(TRIM(setor)) LIKE ?
            )
            AND (is_deleted = 0 OR is_deleted IS NULL)
            ORDER BY COALESCE(finalized_at, created_at) DESC
        """, (f'%{setor_nome.lower()}%', f'%{setor_nome.lower()}%'))
        
        rncs = cursor.fetchall()
        print(f"RNCs encontrados: {len(rncs)}")
        
        if rncs:
            # Mostrar alguns exemplos
            print("Primeiros 3 RNCs:")
            for i, rnc in enumerate(rncs[:3]):
                print(f"  {i+1}. {rnc[1]} - {rnc[2]} - {rnc[6]} - {rnc[7]}")
        
        # Dados mensais
        monthly_data = {}
        for rnc in rncs:
            created_at = rnc[10]  # created_at
            if created_at:
                month_key = created_at[:7]  # YYYY-MM
                if month_key not in monthly_data:
                    monthly_data[month_key] = 0
                monthly_data[month_key] += 1
        
        print(f"Dados mensais: {dict(sorted(monthly_data.items()))}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erro ao testar setor {setor}: {e}")
        return False

if __name__ == "__main__":
    print("=== TESTE DA API DE INDICADORES POR SETOR ===")
    
    # Testar conexão com banco
    if test_database_connection():
        print("✅ Conexão com banco OK")
        
        # Testar alguns setores
        setores = ['engenharia', 'producao', 'qualidade']
        for setor in setores:
            test_setor_data(setor)
    else:
        print("❌ Erro na conexão com banco")
