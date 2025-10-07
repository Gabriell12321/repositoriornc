#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para adicionar coluna responsável e atualizar dados
"""

import sqlite3
import re
from datetime import datetime
import os

def add_responsavel_column():
    """Adicionar coluna responsável ao banco de dados"""
    
    print("🔧 Adicionando coluna 'responsavel' ao banco de dados...")
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    try:
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(rncs)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'responsavel' not in columns:
            # Adicionar coluna responsavel
            cursor.execute("ALTER TABLE rncs ADD COLUMN responsavel TEXT")
            print("✅ Coluna 'responsavel' adicionada com sucesso!")
        else:
            print("ℹ️ Coluna 'responsavel' já existe")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Erro ao adicionar coluna: {e}")
    finally:
        conn.close()

def extract_responsavel_from_line(line):
    """Extrair responsável de uma linha do arquivo"""
    
    # Padrão para extrair responsável (entre campos específicos)
    # Baseado no formato: ... RESPONSÁVEL ... INSPETOR ...
    
    # Procurar por padrões de responsável
    patterns = [
        r'([A-Za-zÀ-ÿ\s]+)\s+Ronaldo\s+\d{1,2}/\d{1,2}/\d{4}',  # Nome + Ronaldo + Data
        r'([A-Za-zÀ-ÿ\s]+)\s+\d{1,2}/\d{1,2}/\d{4}',  # Nome + Data
        r'([A-Za-zÀ-ÿ\s]+)\s+[A-Za-zÀ-ÿ\s]+\s+\d{1,2}/\d{1,2}/\d{4}'  # Nome + Nome + Data
    ]
    
    for pattern in patterns:
        match = re.search(pattern, line)
        if match:
            responsavel = match.group(1).strip()
            # Limpar responsável
            if responsavel and len(responsavel) > 2:
                return responsavel
    
    return None

def update_responsavel_from_file():
    """Atualizar responsável das RNCs baseado no arquivo"""
    
    print("📖 Atualizando responsáveis das RNCs...")
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    file_path = "DADOS RNC ATUALIZADO.txt"
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        conn.close()
        return
    
    updated_count = 0
    error_count = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            for line_num, line in enumerate(file, 1):
                # Pular linhas de cabeçalho
                if line_num <= 3:
                    continue
                
                # Extrair número da RNC
                rnc_match = re.match(r'^(\d+)\s+', line)
                if not rnc_match:
                    continue
                
                rnc_number = rnc_match.group(1)
                
                # Extrair responsável
                responsavel = extract_responsavel_from_line(line)
                
                if responsavel:
                    # Atualizar RNC no banco
                    cursor.execute("""
                        UPDATE rncs 
                        SET responsavel = ?, updated_at = ?
                        WHERE rnc_number = ?
                    """, (responsavel, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), rnc_number))
                    
                    if cursor.rowcount > 0:
                        updated_count += 1
                        if updated_count % 1000 == 0:
                            print(f"📊 Atualizadas {updated_count} RNCs...")
                else:
                    error_count += 1
        
        conn.commit()
        
        print(f"\n✅ Atualização concluída!")
        print(f"📊 RNCs atualizadas: {updated_count}")
        print(f"❌ Erros: {error_count}")
        
    except Exception as e:
        print(f"❌ Erro ao processar arquivo: {e}")
    finally:
        conn.close()

def test_responsavel_data():
    """Testar dados de responsável"""
    
    print("🧪 Testando dados de responsável...")
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Verificar responsáveis únicos
    cursor.execute("""
        SELECT responsavel, COUNT(*) as count, SUM(price) as total_value
        FROM rncs 
        WHERE responsavel IS NOT NULL AND responsavel != ''
        GROUP BY responsavel
        ORDER BY total_value DESC
        LIMIT 20
    """)
    
    results = cursor.fetchall()
    
    print("📋 Top 20 Responsáveis por Valor:")
    for responsavel, count, value in results:
        print(f"   👤 {responsavel}: {count} RNCs, R$ {value:,.2f}")
    
    # Verificar departamentos
    cursor.execute("""
        SELECT department, responsavel, COUNT(*) as count, SUM(price) as total_value
        FROM rncs 
        WHERE responsavel IS NOT NULL AND responsavel != ''
        GROUP BY department, responsavel
        ORDER BY department, total_value DESC
        LIMIT 30
    """)
    
    dept_results = cursor.fetchall()
    
    print("\n📋 Responsáveis por Departamento:")
    current_dept = None
    for dept, responsavel, count, value in dept_results:
        if dept != current_dept:
            print(f"\n🏢 {dept}:")
            current_dept = dept
        print(f"   👤 {responsavel}: {count} RNCs, R$ {value:,.2f}")
    
    conn.close()

def main():
    """Função principal"""
    
    print("🚀 Atualizando Sistema de Responsáveis")
    print("="*50)
    
    # 1. Adicionar coluna
    add_responsavel_column()
    print()
    
    # 2. Atualizar dados
    update_responsavel_from_file()
    print()
    
    # 3. Testar dados
    test_responsavel_data()
    print()
    
    print("✅ Processo concluído!")
    print("🔄 Agora o relatório usará o responsável correto!")

if __name__ == "__main__":
    main()
