#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_indicadores_api():
    """Teste da API de indicadores"""
    
    try:
        print("🧪 Testando API de indicadores...")
        
        # Fazer requisição para a API
        response = requests.get('http://localhost:5000/api/indicadores')
        
        print(f"📊 Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API funcionando corretamente!")
            print("\n📋 Dados recebidos:")
            
            # Mostrar KPIs
            if 'kpis' in data:
                kpis = data['kpis']
                print(f"• Total RNCs: {kpis.get('total_rncs', 'N/A')}")
                print(f"• Total Metas: {kpis.get('total_metas', 'N/A')}")
                print(f"• Departamentos Ativos: {kpis.get('active_departments', 'N/A')}")
                print(f"• Eficiência Geral: {kpis.get('overall_efficiency', 'N/A')}%")
            
            # Mostrar departamentos
            if 'departments' in data:
                print(f"\n🏭 Departamentos ({len(data['departments'])}):")
                for dept in data['departments']:
                    print(f"• {dept.get('department', 'N/A')}: Meta={dept.get('meta', 0)}, Realizado={dept.get('realizado', 0)}, Eficiência={dept.get('efficiency', 0)}%")
            
            # Mostrar tendências
            if 'monthly_trends' in data:
                print(f"\n📈 Tendências Mensais ({len(data['monthly_trends'])} meses)")
            
            return True
            
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")
        return False

if __name__ == "__main__":
    test_indicadores_api()
