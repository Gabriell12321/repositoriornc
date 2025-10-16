#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from pathlib import Path

def test_json_loading():
    """Teste direto do carregamento do JSON"""
    
    try:
        print("🧪 Testando carregamento do arquivo JSON...")
        root = Path(__file__).resolve().parents[1]
        data_dir = root / 'data'
        json_file = str((data_dir / 'complete_indicators_data.json') if (data_dir / 'complete_indicators_data.json').exists() else (root / 'complete_indicators_data.json'))
        
        if os.path.exists(json_file):
            print("✅ Arquivo JSON encontrado!")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print("✅ JSON carregado com sucesso!")
            
            # Converter para formato esperado pelo frontend (igual ao endpoint da API)
            result = {
                'kpis': {
                    'total_rncs': data.get('summary', {}).get('total_rncs', 652),
                    'total_metas': data.get('summary', {}).get('total_metas', 912),
                    'active_departments': len(data.get('departments', [])),
                    'overall_efficiency': data.get('summary', {}).get('overall_efficiency', 28.5),
                    'avg_rncs_per_dept': data.get('summary', {}).get('avg_rncs_per_dept', 163.0)
                },
                'departments': [],
                'monthly_trends': data.get('trends', {}).get('monthly', [])
            }
            
            # Processar dados dos departamentos
            departments_data = data.get('departments', {})
            for dept_name, dept_data in departments_data.items():
                if dept_name and isinstance(dept_data, dict):
                    result['departments'].append({
                        'department': dept_name,
                        'meta': dept_data.get('total_meta', 0),
                        'realizado': dept_data.get('total_realizado', 0),
                        'efficiency': dept_data.get('efficiency_percentage', 0)
                    })
            
            print("\n📊 Dados processados:")
            print(f"• Total RNCs: {result['kpis']['total_rncs']}")
            print(f"• Total Metas: {result['kpis']['total_metas']}")
            print(f"• Departamentos Ativos: {result['kpis']['active_departments']}")
            print(f"• Eficiência Geral: {result['kpis']['overall_efficiency']}%")
            
            print(f"\n🏭 Departamentos encontrados ({len(result['departments'])}):")
            for dept in result['departments']:
                print(f"• {dept['department']}: Meta={dept['meta']}, Realizado={dept['realizado']}, Eficiência={dept['efficiency']}%")
            
            print(f"\n📈 Tendências mensais: {len(result['monthly_trends'])} registros")
            
            return True
            
        else:
            print("❌ Arquivo JSON não encontrado!")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao carregar JSON: {e}")
        return False

if __name__ == "__main__":
    test_json_loading()
