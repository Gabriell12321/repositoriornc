#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import os
import glob

print("=== EXTRAÇÃO COMPLETA DE RNC E GARANTIAS ===")

base_folder = r'G:\My Drive\Trabalhos pendentes\rncs\RELATORIO DE NÃO CONFORMIDADE IPPEL\ARQUIVOS PARA PUXAR INFORMAÇÕES PARA O PAINEL'

try:
    # Buscar arquivos de levantamento
    levantamento_files = glob.glob(os.path.join(base_folder, "*Levantamento RNC e Garantias*.ods"))
    
    if levantamento_files:
        latest_file = sorted(levantamento_files, reverse=True)[0]
        print(f"✅ Analisando: {os.path.basename(latest_file)}")
        
        # Ler a aba RNC
        df = pd.read_excel(latest_file, sheet_name='RNC', engine='odf')
        
        # Encontrar onde começam as seções RNC e GARANTIAS
        rnc_start = None
        garantias_start = None
        
        for idx, row in df.iterrows():
            first_col = str(row.iloc[0]).strip().upper()
            if first_col == 'RNC':
                rnc_start = idx
                print(f"📊 Seção RNC encontrada na linha {idx}")
            elif first_col == 'GARANTIAS':
                garantias_start = idx
                print(f"📊 Seção GARANTIAS encontrada na linha {idx}")
        
        if rnc_start is not None:
            print(f"\n🔍 DADOS DE RNC (a partir da linha {rnc_start}):")
            # Pegar dados RNC (próximas linhas após 'RNC')
            rnc_header_idx = rnc_start + 1  # Linha com cabeçalhos
            rnc_data_start = rnc_start + 2  # Início dos dados
            
            # Determinar onde os dados RNC terminam
            rnc_data_end = garantias_start if garantias_start else len(df)
            
            # Extrair cabeçalhos e dados RNC
            headers = df.iloc[rnc_header_idx].tolist()
            rnc_data = df.iloc[rnc_data_start:rnc_data_end]
            
            print(f"   📋 Cabeçalhos: {headers}")
            print(f"   📊 {len(rnc_data)} linhas de dados")
            print("   📄 Primeiras 3 linhas de dados RNC:")
            print(rnc_data.head(3).to_string())
        
        if garantias_start is not None:
            print(f"\n🔍 DADOS DE GARANTIAS (a partir da linha {garantias_start}):")
            # Pegar dados GARANTIAS (próximas linhas após 'GARANTIAS')
            garantias_header_idx = garantias_start + 1  # Linha com cabeçalhos
            garantias_data_start = garantias_start + 2  # Início dos dados
            
            # Extrair cabeçalhos e dados GARANTIAS
            garantias_headers = df.iloc[garantias_header_idx].tolist()
            garantias_data = df.iloc[garantias_data_start:]
            
            print(f"   📋 Cabeçalhos: {garantias_headers}")
            print(f"   📊 {len(garantias_data)} linhas de dados")
            print("   📄 Primeiras 3 linhas de dados GARANTIAS:")
            print(garantias_data.head(3).to_string())
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
