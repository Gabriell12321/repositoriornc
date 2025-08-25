import pandas as pd
import os
from pathlib import Path

def analyze_ods_files():
    """Analisa as planilhas ODS para entender sua estrutura"""
    base_path = "ARQUIVOS PARA PUXAR INFORMAÇÕES PARA O PAINEL"
    
    # Lista dos anos para processar (16-25)
    years = range(16, 26)
    
    print("🔍 Analisando planilhas ODS...")
    print("=" * 60)
    
    for year in years:
        file_path = f"{base_path}/Levantamento RNC e Garantias {year}.ods"
        
        if os.path.exists(file_path):
            try:
                print(f"\n📄 Analisando: {file_path}")
                
                # Tentar ler com diferentes engines
                try:
                    df = pd.read_excel(file_path, engine='odf')
                except:
                    # Se falhar, tentar sem especificar engine
                    df = pd.read_excel(file_path)
                
                print(f"   📊 Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
                print(f"   📋 Colunas: {list(df.columns)}")
                
                # Mostrar primeiras linhas não vazias
                non_empty = df.dropna(how='all').head(3)
                if not non_empty.empty:
                    print(f"   📝 Primeiras linhas:")
                    for idx, row in non_empty.iterrows():
                        print(f"      Linha {idx}: {row.tolist()}")
                
                # Verificar se existe estrutura de meses
                month_cols = [col for col in df.columns if any(month in str(col).lower() for month in ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'])]
                if month_cols:
                    print(f"   📅 Colunas de meses encontradas: {month_cols}")
                
                # Verificar se existe estrutura de departamentos
                dept_keywords = ['produção', 'engenharia', 'qualidade', 'comercial', 'compras', 'pcp', 'expedição']
                dept_rows = []
                for idx, row in df.iterrows():
                    row_str = ' '.join([str(val).lower() for val in row.values if pd.notna(val)])
                    if any(keyword in row_str for keyword in dept_keywords):
                        dept_rows.append((idx, row.tolist()))
                
                if dept_rows:
                    print(f"   🏭 Linhas com departamentos encontradas:")
                    for idx, row_data in dept_rows[:3]:  # Mostrar até 3
                        print(f"      Linha {idx}: {row_data}")
                
            except Exception as e:
                print(f"   ❌ Erro ao ler {file_path}: {e}")
        else:
            print(f"   ⚠️ Arquivo não encontrado: {file_path}")
    
    print("\n" + "=" * 60)
    print("✅ Análise concluída!")

if __name__ == "__main__":
    analyze_ods_files()
