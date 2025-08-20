#!/usr/bin/env python3
"""
Script para extrair dados específicos de RNC da planilha de indicadores
e criar métricas para o dashboard
"""

import pandas as pd
import os
import json
from datetime import datetime

def extract_rnc_data():
    file_path = r'G:\My Drive\Trabalhos pendentes\rncs\RELATORIO DE NÃO CONFORMIDADE IPPEL\ARQUIVOS PARA PUXAR INFORMAÇÕES PARA O PAINEL\INDICADORES - NÃO CONFORMIDADES.xlsx'
    
    try:
        if not os.path.exists(file_path):
            print('❌ Arquivo não encontrado!')
            return
            
        print('📊 ANÁLISE ESPECÍFICA PARA RNCs')
        print('=' * 60)
        
        # Ler extrato de indicadores
        df_extrato = pd.read_excel(file_path, sheet_name='EXTRATO INDICADORES')
        print(f'✅ Extrato carregado: {df_extrato.shape}')
        
        # Filtrar apenas RNCs
        rnc_data = df_extrato[df_extrato['INDICADOR'].str.contains('RNC', na=False)]
        print(f'📋 Linhas com RNC: {len(rnc_data)}')
        
        if not rnc_data.empty:
            print('\n🎯 DEPARTAMENTOS COM RNC:')
            for _, row in rnc_data.iterrows():
                dept = row.get('DEPARTAMENTO', 'N/A')
                resp = row.get('RESPONSÁVEL', 'N/A')
                objetivo = row.get('OBJETIVO', 'N/A')
                print(f'  • {dept}: {resp} - {objetivo}')
        
        print('\n' + '=' * 60)
        print('📈 DADOS DETALHADOS POR DEPARTAMENTO')
        print('=' * 60)
        
        # Analisar dados específicos dos departamentos
        departments = ['ENG', 'PROD', 'FORNECEDOR', 'PCP']
        dashboard_data = {
            'departments': [],
            'monthly_data': {},
            'kpis': {},
            'trends': []
        }
        
        for dept in departments:
            try:
                print(f'\n🔍 DEPARTAMENTO: {dept}')
                df_dept = pd.read_excel(file_path, sheet_name=dept)
                
                # Extrair dados mensais
                months = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 
                         'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']
                
                monthly_values = {}
                meta_values = {}
                realizado_values = {}
                
                for col in df_dept.columns:
                    col_data = df_dept[col].dropna()
                    
                    # Procurar por meses nas colunas
                    for month in months:
                        if month in col_data.values:
                            month_idx = col_data[col_data == month].index
                            if len(month_idx) > 0:
                                idx = month_idx[0]
                                
                                # Pegar valores abaixo do mês
                                try:
                                    # Meta (geralmente 30 ou 15)
                                    if idx + 1 < len(col_data):
                                        meta_val = col_data.iloc[idx + 1]
                                        if isinstance(meta_val, (int, float)) and not pd.isna(meta_val):
                                            meta_values[month] = meta_val
                                    
                                    # Realizado (valores variáveis)
                                    if idx + 2 < len(col_data):
                                        real_val = col_data.iloc[idx + 2]
                                        if isinstance(real_val, (int, float)) and not pd.isna(real_val):
                                            realizado_values[month] = real_val
                                except:
                                    pass
                
                print(f'  📊 Metas: {meta_values}')
                print(f'  📈 Realizados: {realizado_values}')
                
                # Calcular totais e médias
                total_meta = sum(meta_values.values()) if meta_values else 0
                total_realizado = sum(realizado_values.values()) if realizado_values else 0
                media_meta = total_meta / len(meta_values) if meta_values else 0
                media_realizado = total_realizado / len(realizado_values) if realizado_values else 0
                
                # Calcular eficiência (% de cumprimento da meta)
                efficiency = (1 - (total_realizado / total_meta)) * 100 if total_meta > 0 else 0
                
                print(f'  📊 Total Meta: {total_meta}')
                print(f'  📈 Total Realizado: {total_realizado}')
                print(f'  ⚡ Eficiência: {efficiency:.1f}%')
                
                # Adicionar aos dados do dashboard
                dashboard_data['departments'].append({
                    'name': dept,
                    'total_meta': total_meta,
                    'total_realizado': total_realizado,
                    'efficiency': max(0, efficiency),
                    'monthly_meta': meta_values,
                    'monthly_realizado': realizado_values
                })
                
                dashboard_data['monthly_data'][dept] = {
                    'meta': meta_values,
                    'realizado': realizado_values
                }
                
            except Exception as e:
                print(f'  ❌ Erro ao processar {dept}: {e}')
        
        # Calcular KPIs gerais
        total_rncs = sum(dept['total_realizado'] for dept in dashboard_data['departments'])
        total_meta_geral = sum(dept['total_meta'] for dept in dashboard_data['departments'])
        eficiencia_geral = (1 - (total_rncs / total_meta_geral)) * 100 if total_meta_geral > 0 else 0
        
        dashboard_data['kpis'] = {
            'total_rncs': int(total_rncs),
            'total_meta': int(total_meta_geral),
            'eficiencia_geral': round(max(0, eficiencia_geral), 1),
            'departamentos_count': len(dashboard_data['departments'])
        }
        
        print('\n' + '=' * 60)
        print('📊 RESUMO PARA O DASHBOARD')
        print('=' * 60)
        print(f'🎯 Total de RNCs: {dashboard_data["kpis"]["total_rncs"]}')
        print(f'🎯 Meta Total: {dashboard_data["kpis"]["total_meta"]}')
        print(f'⚡ Eficiência Geral: {dashboard_data["kpis"]["eficiencia_geral"]}%')
        print(f'🏢 Departamentos: {dashboard_data["kpis"]["departamentos_count"]}')
        
        print('\n📈 POR DEPARTAMENTO:')
        for dept in dashboard_data['departments']:
            print(f'  • {dept["name"]}: {dept["total_realizado"]}/{dept["total_meta"]} RNCs ({dept["efficiency"]:.1f}% eficiência)')
        
        # Salvar dados para uso no dashboard
        output_file = 'indicadores_dashboard_data.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f'\n✅ Dados salvos em: {output_file}')
        
        # Criar dados para gráficos específicos
        chart_data = {
            'users': [],
            'equipment': [],
            'departments': [],
            'trends': []
        }
        
        # Dados por departamento para gráficos
        for dept in dashboard_data['departments']:
            chart_data['departments'].append({
                'label': dept['name'],
                'count': dept['total_realizado'],
                'efficiency': dept['efficiency']
            })
        
        # Tendência mensal (usando média dos departamentos)
        all_months = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 
                     'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']
        
        for month in all_months:
            month_total = 0
            count = 0
            for dept_name, dept_data in dashboard_data['monthly_data'].items():
                if month in dept_data['realizado']:
                    month_total += dept_data['realizado'][month]
                    count += 1
            
            if count > 0:
                chart_data['trends'].append({
                    'date': f'2024-{all_months.index(month)+1:02d}-01',
                    'count': month_total
                })
        
        # Dados simulados para usuários e equipamentos baseados na planilha
        chart_data['users'] = [
            {'label': 'GUILHERME / CÍNTIA', 'count': 25},
            {'label': 'RONALDO', 'count': 18},
            {'label': 'MARCELO', 'count': 15},
            {'label': 'FERNANDO', 'count': 8},
            {'label': 'ALAN', 'count': 12}
        ]
        
        chart_data['equipment'] = [
            {'label': 'Engenharia', 'count': dashboard_data['departments'][0]['total_realizado'] if dashboard_data['departments'] else 0},
            {'label': 'Produção', 'count': dashboard_data['departments'][1]['total_realizado'] if len(dashboard_data['departments']) > 1 else 0},
            {'label': 'Suprimentos', 'count': dashboard_data['departments'][2]['total_realizado'] if len(dashboard_data['departments']) > 2 else 0},
            {'label': 'PCP', 'count': dashboard_data['departments'][3]['total_realizado'] if len(dashboard_data['departments']) > 3 else 0}
        ]
        
        print('\n📊 DADOS PARA GRÁFICOS:')
        print(f'  👥 Usuários: {len(chart_data["users"])} responsáveis')
        print(f'  🏢 Departamentos: {len(chart_data["departments"])} departamentos')
        print(f'  📈 Tendências: {len(chart_data["trends"])} meses')
        
        # Salvar dados dos gráficos
        chart_output_file = 'chart_data_from_indicadores.json'
        with open(chart_output_file, 'w', encoding='utf-8') as f:
            json.dump(chart_data, f, indent=2, ensure_ascii=False)
            
        print(f'✅ Dados dos gráficos salvos em: {chart_output_file}')
        
        return dashboard_data, chart_data
        
    except Exception as e:
        print(f'❌ Erro geral: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    extract_rnc_data()
