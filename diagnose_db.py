#!/usr/bin/env python3
"""Script de diagnóstico do banco de dados"""

import sqlite3
import os

DB_PATH = 'ippel_system.db'

print("🔍 Diagnóstico do Banco de Dados IPPEL")
print("=" * 50)

# Verificar se o arquivo existe
if os.path.exists(DB_PATH):
    print(f"✅ Banco de dados encontrado: {DB_PATH}")
    print(f"📏 Tamanho do arquivo: {os.path.getsize(DB_PATH)} bytes")
else:
    print(f"❌ Banco de dados não encontrado: {DB_PATH}")
    exit(1)

try:
    # Conectar ao banco
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Listar todas as tabelas
    print("\n📊 Tabelas no banco:")
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cur.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"  - {table_name}")
        
        # Contar registros em cada tabela
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cur.fetchone()[0]
            print(f"    → {count} registros")
            
            # Se for rnc_reports, mostrar detalhes
            if table_name == 'rnc_reports':
                print("    📋 Estrutura da tabela rnc_reports:")
                cur.execute(f"PRAGMA table_info({table_name})")
                columns = cur.fetchall()
                for col in columns:
                    print(f"      {col[1]} ({col[2]})")
                
                if count > 0:
                    print("    📄 Primeiros registros:")
                    cur.execute("SELECT id, rnc_number, title, status FROM rnc_reports LIMIT 3")
                    rows = cur.fetchall()
                    for row in rows:
                        print(f"      ID: {row[0]}, RNC: {row[1]}, Título: {row[2]}, Status: {row[3]}")
                        
        except Exception as e:
            print(f"    ❌ Erro ao ler tabela {table_name}: {e}")
    
    conn.close()
    print("\n✅ Diagnóstico concluído!")
    
except Exception as e:
    print(f"❌ Erro ao acessar banco: {e}")
