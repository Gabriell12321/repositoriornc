#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para atualizar RNCs do arquivo "DADOS RNC ATUALIZADO.txt"
Processa todas as RNCs e marca como finalizadas no banco de dados
"""

import sqlite3
import re
from datetime import datetime
import os
import sys

def parse_rnc_line(line):
    """Parse uma linha do arquivo de dados RNC"""
    if len(line.strip()) < 50:  # Linha muito pequena, provavelmente cabeçalho
        return None
    
    # Padrão para extrair dados da linha
    # Formato: Nº RNC | DESENHO | MP | REVISÃO | POS | CV | EQUIPAMENTO | CONJUNTO | MODELO | DESCRIÇÃO | QUANTIDADE | CLIENTE | MATERIAL | ORDEM | RESPONSÁVEL | INSPETOR | DATA | ÁREA | SETOR | DESCRIÇÃO RNC | INSTRUÇÃO | CAUSA | JUSTIFICATIVA | VALOR
    
    # Extrair número da RNC (primeira coluna)
    rnc_match = re.match(r'^(\d+)\s+', line)
    if not rnc_match:
        return None
    
    rnc_number = rnc_match.group(1)
    
    # Extrair valor (última coluna)
    valor_match = re.search(r'R\$\s*([\d,]+\.?\d*)', line)
    valor = 0.0
    if valor_match:
        valor_str = valor_match.group(1).replace(',', '.')
        try:
            valor = float(valor_str)
        except ValueError:
            valor = 0.0
    
    # Extrair data
    data_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', line)
    data_emissao = None
    if data_match:
        try:
            data_str = data_match.group(1)
            data_emissao = datetime.strptime(data_str, '%m/%d/%Y').strftime('%Y-%m-%d')
        except ValueError:
            data_emissao = None
    
    # Extrair responsável (nome antes de "Ronaldo")
    responsavel_match = re.search(r'([A-Za-zÀ-ÿ\s]+)\s+Ronaldo', line)
    responsavel = "Sistema"
    if responsavel_match:
        responsavel = responsavel_match.group(1).strip()
    
    # Extrair área responsável
    areas = ['Engenharia', 'Produção', 'Compras', 'Qualidade', 'TI', 'Administração', 'Terceiros']
    area_responsavel = "Engenharia"  # Padrão
    for area in areas:
        if area in line:
            area_responsavel = area
            break
    
    # Extrair descrição da RNC (entre aspas ou após certos padrões)
    descricao_match = re.search(r'(?:DESCRIÇÃO DA RNC|RNC)\s+(.+?)(?:\s+INSTRUÇÃO|R\$\s*\d|$)', line, re.IGNORECASE)
    descricao = "RNC processada automaticamente"
    if descricao_match:
        descricao = descricao_match.group(1).strip()
        if len(descricao) > 200:
            descricao = descricao[:200] + "..."
    
    return {
        'rnc_number': rnc_number,
        'title': f"RNC {rnc_number}",
        'description': descricao,
        'equipment': "Equipamento não especificado",
        'client': "Cliente não especificado",
        'priority': 'Média',
        'status': 'Finalizado',
        'price': valor,
        'creator_name': responsavel,
        'creator_department': area_responsavel,
        'created_at': data_emissao or datetime.now().strftime('%Y-%m-%d'),
        'finalized_at': data_emissao or datetime.now().strftime('%Y-%m-%d'),
        'is_deleted': 0
    }

def update_database():
    """Atualizar banco de dados com RNCs do arquivo"""
    
    # Conectar ao banco
    db_path = 'database.db'
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar se a tabela rncs existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rncs'")
    if not cursor.fetchone():
        print("❌ Tabela 'rncs' não encontrada no banco de dados")
        conn.close()
        return
    
    # Ler arquivo de dados
    file_path = "DADOS RNC ATUALIZADO.txt"
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        conn.close()
        return
    
    print(f"📖 Processando arquivo: {file_path}")
    
    # Contadores
    total_lines = 0
    processed_rncs = 0
    updated_rncs = 0
    new_rncs = 0
    errors = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            for line_num, line in enumerate(file, 1):
                total_lines += 1
                
                # Pular linhas de cabeçalho ou muito pequenas
                if line_num <= 3 or len(line.strip()) < 20:
                    continue
                
                # Processar linha
                rnc_data = parse_rnc_line(line)
                if not rnc_data:
                    continue
                
                processed_rncs += 1
                
                # Verificar se RNC já existe
                cursor.execute("SELECT id FROM rncs WHERE rnc_number = ?", (rnc_data['rnc_number'],))
                existing_rnc = cursor.fetchone()
                
                if existing_rnc:
                    # Atualizar RNC existente
                    cursor.execute("""
                        UPDATE rncs SET 
                        title = ?, description = ?, equipment = ?, client = ?, 
                        priority = ?, status = ?, price = ?, creator_name = ?, 
                        creator_department = ?, finalized_at = ?, updated_at = ?
                        WHERE rnc_number = ?
                    """, (
                        rnc_data['title'], rnc_data['description'], rnc_data['equipment'],
                        rnc_data['client'], rnc_data['priority'], rnc_data['status'],
                        rnc_data['price'], rnc_data['creator_name'], rnc_data['creator_department'],
                        rnc_data['finalized_at'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        rnc_data['rnc_number']
                    ))
                    updated_rncs += 1
                else:
                    # Inserir nova RNC
                    cursor.execute("""
                        INSERT INTO rncs (
                            rnc_number, title, description, equipment, client, 
                            priority, status, user_id, created_at, updated_at, 
                            finalized_at, is_deleted, price, creator_name, creator_department
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        rnc_data['rnc_number'], rnc_data['title'], rnc_data['description'],
                        rnc_data['equipment'], rnc_data['client'], rnc_data['priority'],
                        rnc_data['status'], 1, rnc_data['created_at'], 
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'), rnc_data['finalized_at'],
                        rnc_data['is_deleted'], rnc_data['price'], rnc_data['creator_name'],
                        rnc_data['creator_department']
                    ))
                    new_rncs += 1
                
                # Mostrar progresso a cada 1000 linhas
                if processed_rncs % 1000 == 0:
                    print(f"📊 Processadas {processed_rncs} RNCs...")
    
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {e}")
        errors += 1
    
    # Commit das alterações
    conn.commit()
    
    # Estatísticas finais
    print("\n" + "="*50)
    print("📊 RESUMO DA ATUALIZAÇÃO")
    print("="*50)
    print(f"📄 Total de linhas no arquivo: {total_lines}")
    print(f"🔍 RNCs processadas: {processed_rncs}")
    print(f"✅ RNCs atualizadas: {updated_rncs}")
    print(f"🆕 RNCs novas: {new_rncs}")
    print(f"❌ Erros: {errors}")
    
    # Verificar total de RNCs no banco
    cursor.execute("SELECT COUNT(*) FROM rncs")
    total_rncs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM rncs WHERE status = 'Finalizado'")
    finalized_rncs = cursor.fetchone()[0]
    
    print(f"📊 Total de RNCs no banco: {total_rncs}")
    print(f"✅ RNCs finalizadas: {finalized_rncs}")
    print("="*50)
    
    conn.close()
    print("✅ Atualização concluída!")

if __name__ == "__main__":
    print("🚀 Iniciando atualização de RNCs do arquivo...")
    update_database()
