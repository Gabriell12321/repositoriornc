#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import os
import glob

print("=== ANÁLISE DO CONTEÚDO DA ABA RNC ===")

base_folder = r'G:\My Drive\Trabalhos pendentes\rncs\RELATORIO DE NÃO CONFORMIDADE IPPEL\ARQUIVOS PARA PUXAR INFORMAÇÕES PARA O PAINEL'

try:
    # Buscar arquivos de levantamento
    levantamento_files = glob.glob(os.path.join(base_folder, "*Levantamento RNC e Garantias*.ods"))
    
    if levantamento_files:
        latest_file = sorted(levantamento_files, reverse=True)[0]
        print(f"✅ Analisando: {os.path.basename(latest_file)}")
        
        # Ler a aba RNC
        df = pd.read_excel(latest_file, sheet_name='RNC', engine='odf')
        print(f"📊 Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
        print(f"📋 Colunas: {list(df.columns)}")
        
        # Procurar por colunas que possam indicar tipo (RNC vs Garantia)
        for col in df.columns:
            if 'TIPO' in str(col).upper() or 'GARANTIA' in str(col).upper() or 'CATEGORY' in str(col).upper():
                print(f"\n🔍 Coluna interessante encontrada: {col}")
                print(f"   Valores únicos: {df[col].unique()[:10]}")  # Primeiros 10 valores únicos
        
        # Procurar por 'garantia' em qualquer lugar dos dados
        print(f"\n🔍 Procurando 'garantia' em todas as colunas de texto:")
        garantia_found = False
        for col in df.columns:
            if df[col].dtype == 'object':  # colunas de texto
                garantia_refs = df[df[col].str.contains('GARANTIA', case=False, na=False)]
                if not garantia_refs.empty:
                    garantia_found = True
                    print(f"✅ Encontrado na coluna '{col}': {len(garantia_refs)} registros")
                    print(f"   Primeiros exemplos:")
                    for idx, row in garantia_refs.head(3).iterrows():
                        print(f"   - {row[col]}")
        
        if not garantia_found:
            print("❌ Não encontrado referências diretas a 'GARANTIA'")
        
        # Mostrar algumas linhas de exemplo
        print(f"\n📄 Primeiras 5 linhas:")
        print(df.head(5).to_string())
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
