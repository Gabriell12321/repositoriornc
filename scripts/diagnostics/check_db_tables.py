#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_database_tables():
    """Verificar tabelas no banco de dados"""
    
    try:
        print("🔍 Verificando tabelas no banco de dados...")
        
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"📊 Tabelas encontradas ({len(tables)}):")
        for table in tables:
            print(f"• {table[0]}")
            
            # Contar registros em cada tabela
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"  - Registros: {count}")
                
                # Se for uma tabela de RNC, mostrar estrutura
                if 'rnc' in table[0].lower():
                    cursor.execute(f"PRAGMA table_info({table[0]})")
                    columns = cursor.fetchall()
                    print(f"  - Colunas: {[col[1] for col in columns]}")
                    
            except Exception as e:
                print(f"  - Erro ao contar: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")

if __name__ == "__main__":
    check_database_tables()
