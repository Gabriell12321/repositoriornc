#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import os

print("=== ANÁLISE DAS ABAS DO ARQUIVO PRINCIPAL ===")

file_path = r'G:\My Drive\Trabalhos pendentes\rncs\RELATORIO DE NÃO CONFORMIDADE IPPEL\ARQUIVOS PARA PUXAR INFORMAÇÕES PARA O PAINEL\INDICADORES - NÃO CONFORMIDADES.xlsx'

try:
    xls = pd.ExcelFile(file_path)
    print(f"✅ Arquivo encontrado")
    print(f"📋 Abas disponíveis: {xls.sheet_names}")
    
    # Analisar algumas abas para entender a estrutura
    abas_para_analisar = ['EXTRATO INDICADORES', 'ENG', 'PROD']
    
    for aba in abas_para_analisar:
        if aba in xls.sheet_names:
            print(f"\n🔍 ANÁLISE DA ABA: {aba}")
            df = pd.read_excel(file_path, sheet_name=aba)
            print(f"   📊 Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
            print(f"   📋 Colunas: {list(df.columns)[:10]}")  # Primeiras 10 colunas
            
            # Mostrar primeiras linhas
            print(f"   📄 Primeiras 3 linhas:")
            print(df.head(3).to_string())
            
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
