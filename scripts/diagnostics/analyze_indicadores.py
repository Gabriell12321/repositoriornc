#!/usr/bin/env python3
"""
Script para analisar a planilha INDICADORES - NÃO CONFORMIDADES.xlsx
"""

import pandas as pd
import os
import sys

def analyze_excel_file():
    file_path = r'G:\My Drive\Trabalhos pendentes\rncs\RELATORIO DE NÃO CONFORMIDADE IPPEL\ARQUIVOS PARA PUXAR INFORMAÇÕES PARA O PAINEL\INDICADORES - NÃO CONFORMIDADES.xlsx'
    
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            print('❌ Arquivo não encontrado!')
            return
            
        print('✅ Arquivo encontrado!')
        print(f'📁 Caminho: {file_path}')
        print('=' * 80)
        
        # Ler todas as abas da planilha
        xls = pd.ExcelFile(file_path)
        print(f'📊 Abas disponíveis: {xls.sheet_names}')
        print('=' * 80)
        
        # Analisar cada aba
        for i, sheet_name in enumerate(xls.sheet_names, 1):
            print(f'\n🔍 ABA {i}: {sheet_name}')
            print('-' * 60)
            
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f'   📏 Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas')
                
                if df.shape[1] > 0:
                    print(f'   📋 Colunas: {list(df.columns)}')
                
                # Mostrar primeiras linhas se houver dados
                if not df.empty and df.shape[1] > 0:
                    print('   📝 Primeiras 5 linhas:')
                    # Limitar exibição para evitar overflow
                    display_df = df.head(5)
                    
                    # Se houver muitas colunas, mostrar apenas as primeiras
                    if display_df.shape[1] > 5:
                        display_df = display_df.iloc[:, :5]
                        print('   (Mostrando apenas as primeiras 5 colunas)')
                    
                    print(display_df.to_string(max_rows=5, max_cols=5))
                    
                    # Mostrar tipos de dados
                    print(f'\n   🏷️  Tipos de dados:')
                    for col, dtype in df.dtypes.items():
                        print(f'      {col}: {dtype}')
                        
                    # Verificar valores únicos em colunas relevantes
                    for col in df.columns:
                        if df[col].dtype == 'object' and len(df[col].unique()) < 20:
                            print(f'\n   🎯 Valores únicos em "{col}": {list(df[col].unique()[:10])}')
                            if len(df[col].unique()) > 10:
                                print(f'      ... e mais {len(df[col].unique()) - 10} valores')
                
                else:
                    print('   ⚠️  Aba vazia ou sem dados válidos')
                    
            except Exception as e:
                print(f'   ❌ Erro ao ler aba "{sheet_name}": {e}')
            
            print('-' * 60)
        
        # Análise consolidada
        print('\n' + '=' * 80)
        print('📈 RESUMO DA ANÁLISE')
        print('=' * 80)
        
        # Procurar indicadores chave
        all_data = {}
        for sheet_name in xls.sheet_names:
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                if not df.empty:
                    all_data[sheet_name] = df
            except:
                continue
                
        # Identificar possíveis KPIs
        print('\n🎯 POSSÍVEIS INDICADORES IDENTIFICADOS:')
        for sheet_name, df in all_data.items():
            print(f'\n📊 {sheet_name}:')
            
            # Procurar colunas numéricas
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                print(f'   📈 Colunas numéricas: {numeric_cols}')
                
                # Calcular estatísticas básicas
                for col in numeric_cols[:3]:  # Limitar para evitar spam
                    if not df[col].isna().all():
                        print(f'      {col}: Min={df[col].min():.2f}, Max={df[col].max():.2f}, Média={df[col].mean():.2f}')
            
            # Procurar colunas de datas
            date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
            if date_cols:
                print(f'   📅 Colunas de data: {date_cols}')
                
            # Procurar colunas categóricas importantes
            text_cols = df.select_dtypes(include=['object']).columns.tolist()
            important_keywords = ['status', 'prioridade', 'departamento', 'setor', 'tipo', 'categoria']
            relevant_cols = [col for col in text_cols if any(keyword in col.lower() for keyword in important_keywords)]
            if relevant_cols:
                print(f'   🏷️  Colunas categóricas relevantes: {relevant_cols}')
        
        print('\n✅ Análise concluída!')
        
    except Exception as e:
        print(f'❌ Erro geral ao analisar planilha: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    analyze_excel_file()
