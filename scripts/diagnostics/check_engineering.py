#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
from datetime import datetime

def check_engineering_data():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    print("=== VERIFICANDO DADOS DE ENGENHARIA ===\n")
    
    # 1. Verificar estrutura da tabela rncs
    print("1. ESTRUTURA DA TABELA RNCs:")
    cursor.execute("PRAGMA table_info(rncs)")
    columns = cursor.fetchall()
    for col in columns:
        print(f"   - {col[1]} ({col[2]})")
    
    # 2. Verificar todos os setores únicos
    print("\n2. SETORES ÚNICOS NO BANCO:")
    cursor.execute("SELECT DISTINCT setor FROM rncs WHERE setor IS NOT NULL ORDER BY setor")
    setores = cursor.fetchall()
    for setor in setores:
        print(f"   - {setor[0]}")
    
    # 3. Buscar RNCs que podem ser de Engenharia (várias formas)
    print("\n3. BUSCANDO RNCs DE ENGENHARIA:")
    
    # Busca case-insensitive por engenharia em vários campos
    cursor.execute("""
        SELECT id, titulo, setor, equipamento, responsavel, data_finalizacao, status
        FROM rncs 
        WHERE LOWER(setor) LIKE '%engenharia%' 
           OR LOWER(equipamento) LIKE '%engenharia%' 
           OR LOWER(responsavel) LIKE '%engenharia%'
           OR LOWER(titulo) LIKE '%engenharia%'
           OR setor = 'Engenharia'
        ORDER BY id DESC
        LIMIT 10
    """)
    rncs_eng = cursor.fetchall()
    
    print(f"   Encontradas {len(rncs_eng)} RNCs relacionadas à Engenharia:")
    for rnc in rncs_eng:
        print(f"   ID: {rnc[0]} | Título: {rnc[1][:40]}... | Setor: {rnc[2]} | Status: {rnc[6]}")
    
    # 4. Verificar se existe tabela de setores separada
    print("\n4. VERIFICANDO TABELAS DE SETORES:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%setor%'")
    tabelas_setor = cursor.fetchall()
    for tabela in tabelas_setor:
        print(f"   - Tabela encontrada: {tabela[0]}")
        
    # 5. Verificar RNCs recentes para debug
    print("\n5. ÚLTIMAS 5 RNCs CADASTRADAS:")
    cursor.execute("""
        SELECT id, titulo, setor, equipamento, responsavel, status
        FROM rncs 
        ORDER BY id DESC 
        LIMIT 5
    """)
    ultimas_rncs = cursor.fetchall()
    for rnc in ultimas_rncs:
        print(f"   ID: {rnc[0]} | Título: {rnc[1][:30]}... | Setor: {rnc[2]} | Status: {rnc[5]}")
    
    # 6. Verificar padrões de nomenclatura de setores
    print("\n6. CONTAGEM POR SETOR (TOP 10):")
    cursor.execute("""
        SELECT setor, COUNT(*) as total
        FROM rncs 
        WHERE setor IS NOT NULL
        GROUP BY setor
        ORDER BY total DESC
        LIMIT 10
    """)
    top_setores = cursor.fetchall()
    for setor in top_setores:
        print(f"   {setor[0]}: {setor[1]} RNCs")
    
    # 7. Verificar dados do dashboard atual
    print("\n7. TESTANDO ENDPOINT DO DASHBOARD:")
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Finalizado' THEN 1 ELSE 0 END) as finalizados,
                SUM(CASE WHEN status = 'Aberto' THEN 1 ELSE 0 END) as abertos
            FROM rncs 
            WHERE LOWER(setor) LIKE '%engenharia%' OR setor = 'Engenharia'
        """)
        stats = cursor.fetchone()
        print(f"   Total Engenharia: {stats[0]}")
        print(f"   Finalizados: {stats[1]}")
        print(f"   Abertos: {stats[2]}")
    except Exception as e:
        print(f"   Erro ao calcular stats: {e}")
    
    conn.close()

if __name__ == "__main__":
    check_engineering_data()
