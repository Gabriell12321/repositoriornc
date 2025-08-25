#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from collections import Counter

def analyze_sectors():
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        print("=== ANALISANDO SETORES NAS RNCs ===")
        
        # Verificar se existe campo de setor nas RNCs
        cursor.execute('PRAGMA table_info(rncs)')
        columns = cursor.fetchall()
        print("Colunas da tabela RNCs:")
        for col in columns:
            if 'setor' in col[1].lower() or 'sector' in col[1].lower() or 'department' in col[1].lower():
                print(f"  -> {col[1]} ({col[2]})")
        
        # Verificar se existe tabela de setores
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%sector%' OR name LIKE '%setor%'")
        sector_tables = cursor.fetchall()
        print(f"\nTabelas relacionadas a setores: {sector_tables}")
        
        # Verificar tabela sectors
        try:
            cursor.execute('SELECT * FROM sectors LIMIT 10')
            sectors_data = cursor.fetchall()
            print(f"\nDados na tabela 'sectors' (primeiros 10):")
            for sector in sectors_data:
                print(f"  {sector}")
        except:
            print("\nTabela 'sectors' não encontrada ou vazia")
        
        # Buscar campos que podem conter informações de setor
        potential_sector_fields = []
        for col in columns:
            col_name = col[1].lower()
            if any(keyword in col_name for keyword in ['setor', 'sector', 'area', 'department', 'responsavel']):
                potential_sector_fields.append(col[1])
        
        print(f"\nCampos potenciais para setor: {potential_sector_fields}")
        
        # Analisar alguns dados da tabela RNCs para ver padrões
        cursor.execute('SELECT * FROM rncs LIMIT 3')
        sample_rncs = cursor.fetchall()
        print(f"\nExemplo de dados das RNCs (primeiras 3):")
        cursor.execute('PRAGMA table_info(rncs)')
        col_names = [col[1] for col in cursor.fetchall()]
        
        for i, rnc in enumerate(sample_rncs):
            print(f"\nRNC {i+1}:")
            for j, value in enumerate(rnc):
                if j < len(col_names):
                    print(f"  {col_names[j]}: {value}")
        
        # Verificar se há informações de setor nos campos de equipamento ou cliente
        print(f"\n=== ANALISANDO EQUIPAMENTOS PARA IDENTIFICAR SETORES ===")
        cursor.execute('''
            SELECT equipment, COUNT(*) as count
            FROM rncs 
            WHERE equipment IS NOT NULL AND equipment != ''
            GROUP BY equipment
            ORDER BY count DESC
            LIMIT 20
        ''')
        equipments = cursor.fetchall()
        print("Top 20 equipamentos:")
        for equipment, count in equipments:
            print(f"  {equipment}: {count} RNCs")
        
        # Verificar clientes
        print(f"\n=== ANALISANDO CLIENTES PARA IDENTIFICAR SETORES ===")
        cursor.execute('''
            SELECT client, COUNT(*) as count
            FROM rncs 
            WHERE client IS NOT NULL AND client != ''
            GROUP BY client
            ORDER BY count DESC
            LIMIT 20
        ''')
        clients = cursor.fetchall()
        print("Top 20 clientes:")
        for client, count in clients:
            print(f"  {client}: {count} RNCs")
        
        # Analisar descrições para palavras-chave de setores
        print(f"\n=== ANALISANDO DESCRIÇÕES PARA PALAVRAS DE SETORES ===")
        cursor.execute('''
            SELECT description
            FROM rncs 
            WHERE description IS NOT NULL AND description != ''
            LIMIT 100
        ''')
        descriptions = cursor.fetchall()
        
        # Palavras-chave para identificar setores
        sector_keywords = {
            'Produção': ['produção', 'produção', 'linha', 'fabricação', 'montagem', 'operação'],
            'Manutenção': ['manutenção', 'reparo', 'manutenção preventiva', 'manutenção corretiva', 'quebra'],
            'Qualidade': ['qualidade', 'inspeção', 'teste', 'controle', 'auditoria', 'não conformidade'],
            'Engenharia': ['projeto', 'desenho', 'especificação', 'desenvolvimento', 'modificação'],
            'Logística': ['expedição', 'estoque', 'armazenamento', 'transporte', 'recebimento'],
            'Compras': ['fornecedor', 'compra', 'aquisição', 'material'],
            'Vendas': ['venda', 'comercial', 'cliente', 'pedido'],
            'Administrativo': ['administrativo', 'gestão', 'documentação', 'processo']
        }
        
        sector_counts = {sector: 0 for sector in sector_keywords.keys()}
        
        for desc_tuple in descriptions:
            description = desc_tuple[0].lower() if desc_tuple[0] else ""
            for sector, keywords in sector_keywords.items():
                if any(keyword in description for keyword in keywords):
                    sector_counts[sector] += 1
        
        print("Setores identificados nas descrições (amostra de 100 RNCs):")
        for sector, count in sorted(sector_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {sector}: {count} menções")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro durante a análise: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_sectors()
