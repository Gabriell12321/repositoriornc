#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import os
import glob

print("=== PROCURANDO DADOS DE GARANTIA NOS ARQUIVOS DE LEVANTAMENTO ===")

base_folder = r'G:\My Drive\Trabalhos pendentes\rncs\RELATORIO DE NÃO CONFORMIDADE IPPEL\ARQUIVOS PARA PUXAR INFORMAÇÕES PARA O PAINEL'

try:
    # Buscar arquivos de levantamento
    levantamento_files = glob.glob(os.path.join(base_folder, "*Levantamento RNC e Garantias*.ods"))
    
    if not levantamento_files:
        print("❌ Nenhum arquivo de levantamento encontrado!")
    else:
        print(f"📋 Arquivos encontrados: {len(levantamento_files)}")
        
        # Pegar o mais recente
        latest_file = sorted(levantamento_files, reverse=True)[0]
        print(f"✅ Analisando: {os.path.basename(latest_file)}")
        
        # Ler o arquivo (tentando diferentes engines para .ods)
        try:
            xls = pd.ExcelFile(latest_file, engine='odf')
            print(f"📋 Abas disponíveis: {xls.sheet_names}")
            
            # Procurar por abas que contenham 'GARANTIA'
            garantia_sheets = [sheet for sheet in xls.sheet_names if 'GARANTIA' in sheet.upper()]
            rnc_sheets = [sheet for sheet in xls.sheet_names if 'RNC' in sheet.upper()]
            
            print(f"\n🔍 Abas com 'GARANTIA': {garantia_sheets}")
            print(f"🔍 Abas com 'RNC': {rnc_sheets}")
            
            # Analisar uma aba de exemplo se existir
            if garantia_sheets:
                print(f"\n📊 ANÁLISE DA ABA DE GARANTIA: {garantia_sheets[0]}")
                df = pd.read_excel(latest_file, sheet_name=garantia_sheets[0], engine='odf')
                print(f"   📊 Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
                print(f"   📋 Colunas: {list(df.columns)}")
                print(f"   📄 Primeiras 3 linhas:")
                print(df.head(3).to_string())
                
        except Exception as e:
            print(f"❌ Erro ao ler arquivo .ods: {e}")
            print("💡 Tentando com engine padrão...")
            try:
                # Tentar com engine padrão (pode funcionar se LibreOffice estiver instalado)
                df = pd.read_excel(latest_file)
                print(f"✅ Conseguiu ler com engine padrão")
            except Exception as e2:
                print(f"❌ Também falhou: {e2}")
                
except Exception as e:
    print(f"❌ Erro geral: {e}")
    import traceback
    traceback.print_exc()
