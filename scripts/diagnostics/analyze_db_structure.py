#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para analisar a estrutura completa do banco de dados
"""

import sqlite3

def analyze_database_structure():
    """Analisa e documenta a estrutura completa do banco de dados."""
    
    print("=" * 80)
    print("ANÁLISE COMPLETA DA ESTRUTURA DO BANCO DE DADOS - SISTEMA RNC IPPEL")
    print("=" * 80)
    
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Obter todas as tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"\n📊 TOTAL DE TABELAS: {len(tables)}")
    print("=" * 50)
    
    for table in tables:
        table_name = table[0]
        print(f"\n🏷️  TABELA: {table_name.upper()}")
        print("-" * 40)
        
        # Obter schema da tabela
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print("COLUNAS:")
        for col in columns:
            col_id, name, type_name, not_null, default_val, pk = col
            pk_str = " 🔑" if pk else ""
            not_null_str = " (NOT NULL)" if not_null else ""
            default_str = f" DEFAULT {default_val}" if default_val else ""
            print(f"  {col_id:2}: {name:20} | {type_name:15} {not_null_str}{default_str}{pk_str}")
        
        # Contar registros
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"REGISTROS: {count}")
        except Exception as e:
            print(f"REGISTROS: Erro ao contar - {e}")
        
        # Obter foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({table_name})")
        fks = cursor.fetchall()
        if fks:
            print("FOREIGN KEYS:")
            for fk in fks:
                id_fk, seq, table_ref, from_col, to_col, on_update, on_delete, match = fk
                print(f"  {from_col} → {table_ref}.{to_col}")
        
        # Obter indexes
        cursor.execute(f"PRAGMA index_list({table_name})")
        indexes = cursor.fetchall()
        if indexes:
            print("ÍNDICES:")
            for idx in indexes:
                seq, name, unique, origin, partial = idx
                unique_str = " (UNIQUE)" if unique else ""
                print(f"  {name}{unique_str}")
    
    print("\n" + "=" * 80)
    print("ANÁLISE CONCLUÍDA")
    print("=" * 80)
    
    conn.close()

if __name__ == "__main__":
    analyze_database_structure()
