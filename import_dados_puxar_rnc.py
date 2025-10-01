#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE IMPORTAÇÃO - DADOS PUXAR RNC
Processa o arquivo "DADOS PUXAR RNC.txt" e importa para o banco IPPEL
"""

import sqlite3
import re
import csv
from datetime import datetime
import os
import sys

def clean_text(text):
    """Remove caracteres especiais e corrige encoding"""
    if not text:
        return ""
    
    # Corrigir problemas de encoding
    replacements = {
        'N�': 'Nº',
        'REVIS�O': 'REVISÃO',
        'DESCRI��O': 'DESCRIÇÃO',
        'RESPONS�VEL': 'RESPONSÁVEL',
        '�REA': 'ÁREA',
        'INSTRU��O': 'INSTRUÇÃO',
        'Produ��o': 'Produção',
        'Rebobinadeira': 'Rebobinadeira',
        'Rebobianadeira': 'Rebobinadeira',
        'Rebobiandeira': 'Rebobinadeira',
        'Igua�u': 'Iguaçu',
        'a��o': 'ação',
        'indica��o': 'indicação',
        'fura��o': 'furação',
        'altera��o': 'alteração',
        'Altera��o': 'Alteração',
        'modifica��o': 'modificação',
        'dimens�es': 'dimensões',
        'posi��o': 'posição',
        'posi��es': 'posições',
        'di�metro': 'diâmetro',
        'corre��o': 'correção',
        'refrigera��o': 'refrigeração',
        'Amplia��o': 'Ampliação',
        'ajsute': 'ajuste',
        'usiangem': 'usinagem',
        'Acr�scimo': 'Acréscimo',
        'Acr�scimp': 'Acréscimo',
        'transportadoras': 'transportadoras',
        'trasnportadoras': 'transportadoras',
        'supeiror': 'superior',
        'expessura': 'espessura',
        'Ataualizado': 'Atualizado',
        'adi��o': 'adição',
        'Cil�ndrica': 'Cilíndrica',
        'rolaemnto': 'rolamento'
    }
    
    text = str(text)
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text.strip()

def parse_date(date_str):
    """Converte data do formato DD-MMM-YY para YYYY-MM-DD"""
    if not date_str or date_str.strip() == '':
        return None
    
    try:
        # Mapear meses em português para números
        months = {
            'Jan': '01', 'Fev': '02', 'Mar': '03', 'Abr': '04',
            'Mai': '05', 'Jun': '06', 'Jul': '07', 'Ago': '08',
            'Set': '09', 'Out': '10', 'Nov': '11', 'Dez': '12'
        }
        
        # Exemplo: "02-Jan-23" -> "2023-01-02"
        parts = date_str.split('-')
        if len(parts) == 3:
            day = parts[0].zfill(2)
            month = months.get(parts[1], '01')
            year = '20' + parts[2] if len(parts[2]) == 2 else parts[2]
            return f"{year}-{month}-{day}"
    except:
        pass
    
    return None

def parse_value(value_str):
    """Extrai valor monetário do texto"""
    if not value_str:
        return 0.0
    
    # Buscar padrão R$ XXX,XX ou R$ X.XXX,XX
    value_match = re.search(r'R\$\s*([\d.,]+)', str(value_str))
    if value_match:
        value_text = value_match.group(1)
        # Remover pontos (milhares) e converter vírgula para ponto (decimal)
        value_text = value_text.replace('.', '').replace(',', '.')
        try:
            return float(value_text)
        except:
            return 0.0
    
    return 0.0

def process_rnc_data():
    """Processa o arquivo de dados e importa para o banco"""
    
    file_path = r'DADOS PUXAR RNC\DADOS PUXAR RNC.txt'
    
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        return
    
    print("🚀 INICIANDO IMPORTAÇÃO DOS DADOS PUXAR RNC")
    print("=" * 60)
    
    # Conectar ao banco
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Estatísticas
    total_lines = 0
    imported_count = 0
    error_count = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            # Ler cabeçalho
            header = file.readline().strip()
            print(f"📋 Cabeçalho: {clean_text(header)[:100]}...")
            
            total_lines = 1
            
            for line_num, line in enumerate(file, 2):
                total_lines += 1
                
                if not line.strip():
                    continue
                
                try:
                    # Dividir linha por tabs
                    columns = line.split('\t')
                    
                    if len(columns) < 20:  # Linha incompleta
                        continue
                    
                    # Extrair dados principais
                    rnc_number = clean_text(columns[0])
                    if not rnc_number or not rnc_number.isdigit():
                        continue
                    
                    desenho = clean_text(columns[1])
                    equipamento = clean_text(columns[6])
                    conjunto = clean_text(columns[7])
                    modelo = clean_text(columns[8])
                    descricao_desenho = clean_text(columns[9])
                    quantidade = clean_text(columns[10])
                    cliente = clean_text(columns[11])
                    material = clean_text(columns[12])
                    responsavel = clean_text(columns[14])
                    inspetor = clean_text(columns[15])
                    data_emissao = parse_date(clean_text(columns[16]))
                    area_responsavel = clean_text(columns[17])
                    setor = clean_text(columns[18])
                    descricao_rnc = clean_text(columns[19])
                    instrucao_retrabalho = clean_text(columns[20]) if len(columns) > 20 else ""
                    causa_rnc = clean_text(columns[21]) if len(columns) > 21 else ""
                    justificativa = clean_text(columns[22]) if len(columns) > 22 else ""
                    valor = parse_value(columns[23]) if len(columns) > 23 else 0.0
                    
                    # Criar título da RNC
                    title = f"RNC {rnc_number} - {equipamento}"
                    if conjunto:
                        title += f" / {conjunto}"
                    
                    # Criar descrição completa
                    description_parts = []
                    if descricao_desenho:
                        description_parts.append(f"Desenho: {descricao_desenho}")
                    if descricao_rnc:
                        description_parts.append(f"RNC: {descricao_rnc}")
                    if causa_rnc:
                        description_parts.append(f"Causa: {causa_rnc}")
                    if justificativa:
                        description_parts.append(f"Justificativa: {justificativa}")
                    
                    description = " | ".join(description_parts)
                    
                    # Determinar prioridade baseada no valor
                    if valor >= 500:
                        priority = "Alta"
                    elif valor >= 200:
                        priority = "Média"
                    else:
                        priority = "Baixa"
                    
                    # Inserir no banco
                    cursor.execute("""
                        INSERT INTO rncs (
                            rnc_number, title, description, equipment, client, priority,
                            status, user_id, price, responsavel, inspetor,
                            setor, material, quantity, drawing, instruction_retrabalho,
                            cause_rnc, action_rnc, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        f"RNC-{rnc_number}",
                        title[:255],  # Limitar tamanho
                        description[:1000],  # Limitar tamanho
                        equipamento[:255],
                        cliente[:255],
                        priority,
                        "Finalizado",  # Status padrão
                        1,  # ID do usuário admin
                        valor,
                        responsavel[:100],
                        inspetor[:100],
                        setor[:100],
                        material[:100],
                        quantidade[:50],
                        desenho[:100],
                        instrucao_retrabalho[:500],
                        causa_rnc[:500],
                        justificativa[:500],  # action_rnc
                        data_emissao or datetime.now().strftime('%Y-%m-%d'),
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ))
                    
                    imported_count += 1
                    
                    # Mostrar progresso
                    if imported_count % 100 == 0:
                        print(f"   📊 Processadas: {imported_count} RNCs...")
                
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:  # Mostrar apenas os primeiros 5 erros
                        print(f"   ⚠️ Erro na linha {line_num}: {str(e)[:100]}")
                    continue
        
        # Commit das transações
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ IMPORTAÇÃO CONCLUÍDA!")
        print("=" * 60)
        print(f"📊 Estatísticas:")
        print(f"   Total de linhas: {total_lines:,}")
        print(f"   RNCs importadas: {imported_count:,}")
        print(f"   Erros: {error_count}")
        print(f"   Taxa de sucesso: {(imported_count/(total_lines-1)*100):.1f}%")
        
        # Verificar dados no banco
        cursor.execute("SELECT COUNT(*) FROM rncs")
        total_db = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(price) FROM rncs")
        total_value = cursor.fetchone()[0] or 0
        
        print(f"\n📈 Dados no banco:")
        print(f"   Total RNCs: {total_db:,}")
        print(f"   Valor total: R$ {total_value:,.2f}")
        
        # Mostrar amostra dos dados importados
        cursor.execute("""
            SELECT rnc_number, title, client, responsavel, price 
            FROM rncs 
            ORDER BY id DESC 
            LIMIT 5
        """)
        sample = cursor.fetchall()
        
        print(f"\n📋 Últimas RNCs importadas:")
        for rnc in sample:
            print(f"   • {rnc[0]}: {rnc[1][:50]}... - R$ {rnc[4]:.2f}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erro durante importação: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()

if __name__ == '__main__':
    # Verificar se há uma adição de coluna necessária
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Adicionar colunas se não existirem
        new_columns = [
            'responsavel TEXT',
            'inspetor TEXT',
            'setor TEXT',
            'material TEXT',
            'quantity TEXT',
            'drawing TEXT',
            'instruction_retrabalho TEXT',
            'cause_rnc TEXT',
            'action_rnc TEXT'
        ]
        
        for col in new_columns:
            try:
                cursor.execute(f"ALTER TABLE rncs ADD COLUMN {col}")
            except sqlite3.OperationalError:
                pass  # Coluna já existe
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"⚠️ Aviso: {e}")
    
    # Executar importação
    process_rnc_data()