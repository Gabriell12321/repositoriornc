#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import os

print("=== PROCURANDO DADOS DE GARANTIA ===")

file_path = r'G:\My Drive\Trabalhos pendentes\rncs\RELATORIO DE NÃO CONFORMIDADE IPPEL\ARQUIVOS PARA PUXAR INFORMAÇÕES PARA O PAINEL\INDICADORES - NÃO CONFORMIDADES.xlsx'

try:
    # Verificar se há dados de garantia na aba EXTRATO INDICADORES
    df_extrato = pd.read_excel(file_path, sheet_name='EXTRATO INDICADORES')
    
    print("🔍 Procurando referências a 'GARANTIA' no EXTRATO INDICADORES:")
    
    # Procurar por garantia em todas as colunas de texto
    for col in df_extrato.columns:
        if df_extrato[col].dtype == 'object':  # colunas de texto
            garantia_refs = df_extrato[df_extrato[col].str.contains('GARANTIA', case=False, na=False)]
            if not garantia_refs.empty:
                print(f"✅ Encontrado na coluna '{col}':")
                for idx, row in garantia_refs.iterrows():
                    print(f"   - Linha {idx}: {row[col]}")
    
    # Verificar todos os indicadores
    print(f"\n📋 TODOS OS INDICADORES ({len(df_extrato)}):")
    for idx, row in df_extrato.iterrows():
        indicador = str(row.get('INDICADOR', ''))
        tipo = str(row.get('TIPO', ''))
        dept = str(row.get('DEPARTAMENTO', ''))
        print(f"   {idx+1:2d}. {tipo} | {dept} | {indicador}")
    
    # Verificar se há outras abas que possam conter dados de garantia
    xls = pd.ExcelFile(file_path)
    print(f"\n🔍 Procurando 'GARANTIA' nos nomes das abas:")
    for sheet in xls.sheet_names:
        if 'GAR' in sheet.upper() or 'GARANTIA' in sheet.upper():
            print(f"   ✅ Encontrado: {sheet}")
        else:
            print(f"   - {sheet}")
            
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
