#!/usr/bin/env python3
"""
Análise da estrutura do banco de dados do sistema IPPEL
"""

import sqlite3
import os

def analyze_database():
    db_path = 'ippel_system.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🗄️  ANÁLISE DO BANCO DE DADOS IPPEL")
        print("=" * 60)
        
        # Obter todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"📊 Total de tabelas: {len(tables)}\n")
        
        for table in tables:
            table_name = table[0]
            print(f"📋 TABELA: {table_name}")
            print("-" * 40)
            
            # Obter estrutura da tabela
            cursor.execute(f'PRAGMA table_info({table_name})')
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, name, type_, notnull, default, pk = col
                pk_indicator = ' 🔑' if pk else ''
                null_indicator = ' [NOT NULL]' if notnull else ''
                default_indicator = f' [DEFAULT: {default}]' if default else ''
                print(f"  └─ {name}: {type_}{pk_indicator}{null_indicator}{default_indicator}")
            
            # Contar registros
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                count = cursor.fetchone()[0]
                print(f"  📊 Registros: {count:,}")
            except Exception as e:
                print(f"  ❌ Erro ao contar registros: {e}")
            
            print()
        
        conn.close()
        print("✅ Análise concluída!")
        
    except Exception as e:
        print(f"❌ Erro ao analisar banco: {e}")

if __name__ == "__main__":
    analyze_database()
