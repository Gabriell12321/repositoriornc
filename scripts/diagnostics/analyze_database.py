#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
from pathlib import Path

def analyze_database_structure():
    """Analisar estrutura completa do banco de dados"""
    
    try:
        print("🔍 Analisando estrutura do banco de dados...")
        
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        analysis = {
            'tables': {},
            'summary': {
                'total_tables': len(tables),
                'rnc_tables': [],
                'main_tables': []
            }
        }
        
        print(f"📊 Total de tabelas encontradas: {len(tables)}")
        print("\n" + "="*60)
        
        for table_tuple in tables:
            table_name = table_tuple[0]
            
            print(f"\n📋 TABELA: {table_name}")
            print("-" * 40)
            
            # Obter estrutura da tabela
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Contar registros
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                record_count = cursor.fetchone()[0]
            except Exception as e:
                record_count = f"Erro: {e}"
            
            table_info = {
                'columns': {},
                'record_count': record_count,
                'has_rnc_relation': False
            }
            
            print(f"📝 Colunas ({len(columns)}):")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, primary_key = col
                table_info['columns'][col_name] = {
                    'type': col_type,
                    'not_null': bool(not_null),
                    'default': default_val,
                    'primary_key': bool(primary_key)
                }
                
                # Verificar se é relacionada a RNC
                if 'rnc' in col_name.lower():
                    table_info['has_rnc_relation'] = True
                
                pk_indicator = " [PK]" if primary_key else ""
                null_indicator = " [NOT NULL]" if not_null else ""
                default_indicator = f" [DEFAULT: {default_val}]" if default_val else ""
                
                print(f"  • {col_name} ({col_type}){pk_indicator}{null_indicator}{default_indicator}")
            
            print(f"📊 Registros: {record_count}")
            
            # Classificar tabelas
            if 'rnc' in table_name.lower():
                analysis['summary']['rnc_tables'].append(table_name)
            else:
                analysis['summary']['main_tables'].append(table_name)
            
            analysis['tables'][table_name] = table_info
            
            # Se for tabela RNC, mostrar alguns exemplos
            if 'rnc' in table_name.lower() and isinstance(record_count, int) and record_count > 0:
                try:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    sample_records = cursor.fetchall()
                    if sample_records:
                        print(f"📄 Exemplos de registros:")
                        for i, record in enumerate(sample_records, 1):
                            print(f"  {i}. {record[:3]}...")  # Mostrar apenas primeiros 3 campos
                except Exception as e:
                    print(f"  ⚠️ Erro ao buscar exemplos: {e}")
        
        conn.close()
        
        # Resumo final
        print("\n" + "="*60)
        print("📋 RESUMO DA ANÁLISE")
        print("="*60)
        print(f"Total de tabelas: {analysis['summary']['total_tables']}")
        print(f"Tabelas relacionadas a RNC: {len(analysis['summary']['rnc_tables'])}")
        print(f"  • {', '.join(analysis['summary']['rnc_tables'])}")
        print(f"Outras tabelas: {len(analysis['summary']['main_tables'])}")
        print(f"  • {', '.join(analysis['summary']['main_tables'])}")
        
        # Identificar problema principal
        print("\n🔍 DIAGNÓSTICO:")
        
        if 'rnc_reports' in analysis['tables']:
            rnc_reports_count = analysis['tables']['rnc_reports']['record_count']
            print(f"✅ Tabela 'rnc_reports' existe com {rnc_reports_count} registros")
        else:
            print("❌ Tabela 'rnc_reports' NÃO encontrada!")
        
        if 'rncs' in analysis['tables']:
            rncs_count = analysis['tables']['rncs']['record_count']
            print(f"✅ Tabela 'rncs' existe com {rncs_count} registros")
        else:
            print("❌ Tabela 'rncs' NÃO encontrada!")
        
        # Salvar análise em arquivo (em data/)
        root = Path(__file__).resolve().parents[2]
        data_dir = root / 'data'
        data_dir.mkdir(parents=True, exist_ok=True)
        out_path = data_dir / 'database_analysis.json'
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)

        print(f"\n💾 Análise salva em '{out_path.relative_to(root)}'")
        return analysis
        
    except Exception as e:
        print(f"❌ Erro durante análise: {e}")
        return None

if __name__ == "__main__":
    analyze_database_structure()
