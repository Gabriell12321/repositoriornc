#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inspecionar o banco de dados SQLite
"""

import sqlite3
import os

def inspect_database():
    db_path = 'ippel_system.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Listar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("📊 ESTRUTURA DO BANCO DE DADOS IPPEL")
        print("=" * 50)
        print(f"📁 Arquivo: {db_path}")
        print(f"📋 Total de tabelas: {len(tables)}")
        print()
        
        for table in tables:
            table_name = table[0]
            print(f"🔹 Tabela: {table_name}")
            
            # Obter schema da tabela
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("   Colunas:")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                pk_mark = " (PK)" if pk else ""
                not_null_mark = " NOT NULL" if not_null else ""
                default_mark = f" DEFAULT {default_val}" if default_val else ""
                print(f"     - {col_name}: {col_type}{pk_mark}{not_null_mark}{default_mark}")
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   📊 Registros: {count}")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao inspecionar banco: {e}")

if __name__ == "__main__":
    inspect_database()
