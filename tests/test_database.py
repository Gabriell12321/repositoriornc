#!/usr/bin/env python3
"""
Script para testar e verificar a estrutura do banco de dados RNC
"""

import sqlite3
import os

DB_PATH = 'ippel_system.db'

def check_database_structure():
    """Verificar a estrutura atual do banco de dados"""
    print("🔍 Verificando estrutura do banco de dados...")
    
    if not os.path.exists(DB_PATH):
        print("❌ Banco de dados não encontrado!")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar se a tabela rncs existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rncs'")
    if not cursor.fetchone():
        print("❌ Tabela 'rncs' não encontrada!")
        return
    
    # Obter informações da tabela rncs
    cursor.execute("PRAGMA table_info(rncs)")
    columns = cursor.fetchall()
    
    print(f"\n📋 Estrutura da tabela 'rncs':")
    print("-" * 60)
    for col in columns:
        print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
    
    # Verificar se as colunas de disposição existem
    disposition_columns = [
        'disposition_usar', 'disposition_retrabalhar', 'disposition_rejeitar',
        'disposition_sucata', 'disposition_devolver_estoque', 'disposition_devolver_fornecedor'
    ]
    
    inspection_columns = [
        'inspection_aprovado', 'inspection_reprovado', 'inspection_ver_rnc'
    ]
    
    signature_columns = [
        'signature_inspection_date', 'signature_engineering_date', 'signature_inspection2_date',
        'signature_inspection_name', 'signature_engineering_name', 'signature_inspection2_name'
    ]
    
    existing_columns = [col[1] for col in columns]
    
    print(f"\n🔍 Verificando colunas de disposição:")
    for col in disposition_columns:
        if col in existing_columns:
            print(f"  ✅ {col}")
        else:
            print(f"  ❌ {col} - FALTANDO!")
    
    print(f"\n🔍 Verificando colunas de inspeção:")
    for col in inspection_columns:
        if col in existing_columns:
            print(f"  ✅ {col}")
        else:
            print(f"  ❌ {col} - FALTANDO!")
    
    print(f"\n🔍 Verificando colunas de assinatura:")
    for col in signature_columns:
        if col in existing_columns:
            print(f"  ✅ {col}")
        else:
            print(f"  ❌ {col} - FALTANDO!")
    
    # Verificar dados existentes
    cursor.execute("SELECT COUNT(*) FROM rncs")
    total_rncs = cursor.fetchone()[0]
    print(f"\n📊 Total de RNCs no banco: {total_rncs}")
    
    if total_rncs > 0:
        print(f"\n📋 Exemplo de dados de um RNC:")
        cursor.execute("SELECT * FROM rncs LIMIT 1")
        rnc_data = cursor.fetchone()
        
        if rnc_data:
            print(f"  ID: {rnc_data[0]}")
            print(f"  Número: {rnc_data[1]}")
            print(f"  Título: {rnc_data[2]}")
            
            # Verificar se há dados de disposição
            if len(rnc_data) > 13:  # Se tem as colunas extras
                print(f"  Disposição - Usar: {rnc_data[13] if len(rnc_data) > 13 else 'N/A'}")
                print(f"  Disposição - Retrabalhar: {rnc_data[14] if len(rnc_data) > 14 else 'N/A'}")
                print(f"  Inspeção - Aprovado: {rnc_data[19] if len(rnc_data) > 19 else 'N/A'}")
                print(f"  Inspeção - Reprovado: {rnc_data[20] if len(rnc_data) > 20 else 'N/A'}")
    
    conn.close()

def add_missing_columns():
    """Adicionar colunas que estão faltando"""
    print("\n🔧 Adicionando colunas que estão faltando...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Lista de colunas para adicionar
    columns_to_add = [
        ('disposition_usar', 'BOOLEAN DEFAULT 0'),
        ('disposition_retrabalhar', 'BOOLEAN DEFAULT 0'),
        ('disposition_rejeitar', 'BOOLEAN DEFAULT 0'),
        ('disposition_sucata', 'BOOLEAN DEFAULT 0'),
        ('disposition_devolver_estoque', 'BOOLEAN DEFAULT 0'),
        ('disposition_devolver_fornecedor', 'BOOLEAN DEFAULT 0'),
        ('inspection_aprovado', 'BOOLEAN DEFAULT 0'),
        ('inspection_reprovado', 'BOOLEAN DEFAULT 0'),
        ('inspection_ver_rnc', 'TEXT'),
        ('signature_inspection_date', 'TEXT'),
        ('signature_engineering_date', 'TEXT'),
        ('signature_inspection2_date', 'TEXT'),
        ('signature_inspection_name', 'TEXT'),
        ('signature_engineering_name', 'TEXT'),
        ('signature_inspection2_name', 'TEXT')
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f'ALTER TABLE rncs ADD COLUMN {col_name} {col_type}')
            print(f"  ✅ Adicionada coluna: {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"  ⚠️ Coluna já existe: {col_name}")
            else:
                print(f"  ❌ Erro ao adicionar {col_name}: {e}")
    
    conn.commit()
    conn.close()
    print("✅ Processo de adição de colunas concluído!")

def test_data_insertion():
    """Testar inserção de dados de disposição e inspeção"""
    print("\n🧪 Testando inserção de dados...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Criar um RNC de teste com dados de disposição
    try:
        cursor.execute('''
            INSERT INTO rncs (
                rnc_number, title, description, equipment, client, priority, status, user_id,
                disposition_usar, disposition_retrabalhar, disposition_rejeitar,
                disposition_sucata, disposition_devolver_estoque, disposition_devolver_fornecedor,
                inspection_aprovado, inspection_reprovado, inspection_ver_rnc,
                signature_inspection_date, signature_engineering_date, signature_inspection2_date,
                signature_inspection_name, signature_engineering_name, signature_inspection2_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'RNC-TEST-001', 'Teste de Disposição', 'Descrição de teste', 'Equipamento Teste', 'Cliente Teste',
            'Alta', 'Pendente', 1,  # user_id = 1 (admin)
            1, 1, 0, 0, 0, 0,  # Disposição: Usar e Retrabalhar marcados
            1, 0, 'RNC-2024-001',  # Inspeção: Aprovado marcado
            '15/01/2024', '16/01/2024', '17/01/2024',  # Datas
            'João Silva', 'Maria Santos', 'Pedro Costa'  # Nomes
        ))
        
        conn.commit()
        print("✅ RNC de teste criado com sucesso!")
        
        # Verificar se os dados foram salvos
        cursor.execute("SELECT * FROM rncs WHERE rnc_number = 'RNC-TEST-001'")
        test_rnc = cursor.fetchone()
        
        if test_rnc:
            print(f"📋 Dados salvos:")
            print(f"  Disposição - Usar: {test_rnc[13]}")
            print(f"  Disposição - Retrabalhar: {test_rnc[14]}")
            print(f"  Inspeção - Aprovado: {test_rnc[19]}")
            print(f"  Inspeção - Ver RNC: {test_rnc[21]}")
            print(f"  Assinatura - Nome: {test_rnc[24]}")
        
    except Exception as e:
        print(f"❌ Erro ao criar RNC de teste: {e}")
    
    conn.close()

if __name__ == "__main__":
    print("🚀 Iniciando verificação do banco de dados...")
    
    check_database_structure()
    
    # Perguntar se quer adicionar colunas faltantes
    response = input("\n❓ Deseja adicionar colunas que estão faltando? (s/n): ")
    if response.lower() in ['s', 'sim', 'y', 'yes']:
        add_missing_columns()
        check_database_structure()  # Verificar novamente
    
    # Perguntar se quer testar inserção
    response = input("\n❓ Deseja testar inserção de dados? (s/n): ")
    if response.lower() in ['s', 'sim', 'y', 'yes']:
        test_data_insertion()
    
    print("\n✅ Verificação concluída!") 