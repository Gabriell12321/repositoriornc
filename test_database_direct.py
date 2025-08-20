#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json

def test_database_direct():
    """Teste direto do banco de dados"""
    
    try:
        print("🔍 Testando conexão direta com o banco...")
        
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Listar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📊 Tabelas disponíveis: {tables}")
        
        # Verificar se rnc_reports existe
        if 'rnc_reports' in tables:
            cursor.execute("SELECT COUNT(*) FROM rnc_reports")
            count = cursor.fetchone()[0]
            print(f"✅ Tabela rnc_reports tem {count} registros")
            
            # Mostrar alguns exemplos
            cursor.execute("SELECT id, rnc_number, title, status FROM rnc_reports LIMIT 5")
            samples = cursor.fetchall()
            print("📄 Exemplos:")
            for sample in samples:
                print(f"  {sample}")
                
        # Verificar se rncs existe
        if 'rncs' in tables:
            cursor.execute("SELECT COUNT(*) FROM rncs")
            count = cursor.fetchone()[0]
            print(f"✅ Tabela rncs tem {count} registros")
            
        # Testar a consulta específica da API
        print("\n🧪 Testando consulta da API...")
        
        if 'rnc_reports' in tables:
            # Testar consulta de contagem
            cursor.execute("SELECT COUNT(*) FROM rnc_reports")
            total_rncs = cursor.fetchone()[0]
            print(f"Total RNCs: {total_rncs}")
            
            # Simular dados para teste
            test_data = {
                'kpis': {
                    'total_rncs': total_rncs,
                    'total_metas': 100,
                    'active_departments': 3,
                    'overall_efficiency': 75.5,
                    'avg_rncs_per_dept': total_rncs / 3 if total_rncs > 0 else 0
                },
                'departments': [
                    {'department': 'PRODUÇÃO', 'meta': 50, 'realizado': 40, 'efficiency': 80.0},
                    {'department': 'ENGENHARIA', 'meta': 30, 'realizado': 25, 'efficiency': 83.3},
                    {'department': 'QUALIDADE', 'meta': 20, 'realizado': 15, 'efficiency': 75.0}
                ],
                'monthly_trends': [
                    {'month': 'JAN', 'total': 10, 'date': '2024-01-01'},
                    {'month': 'FEV', 'total': 12, 'date': '2024-02-01'},
                    {'month': 'MAR', 'total': 8, 'date': '2024-03-01'}
                ]
            }
            
            print("📊 Dados de teste criados:")
            print(json.dumps(test_data, indent=2, ensure_ascii=False))
            
            # Salvar dados de teste
            with open('test_indicadores_data.json', 'w', encoding='utf-8') as f:
                json.dump(test_data, f, indent=2, ensure_ascii=False)
            print("💾 Dados de teste salvos em 'test_indicadores_data.json'")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

if __name__ == "__main__":
    test_database_direct()
