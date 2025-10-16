#!/usr/bin/env python3
"""
Migração: Adicionar suporte a categorias de clientes
Adiciona coluna 'category' na tabela clients SEM apagar dados existentes
"""

import sqlite3
import os
import sys

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = 'instance/rnc.db'

def migrate():
    """Adicionar coluna category à tabela clients"""
    print("🔧 Iniciando migração: Adicionar categorias de clientes...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(clients)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'category' not in columns:
            print("📝 Adicionando coluna 'category' à tabela clients...")
            cursor.execute("""
                ALTER TABLE clients 
                ADD COLUMN category TEXT DEFAULT 'Outros'
            """)
            conn.commit()
            print("✅ Coluna 'category' adicionada com sucesso!")
        else:
            print("ℹ️  Coluna 'category' já existe.")
        
        # Contar clientes existentes
        cursor.execute("SELECT COUNT(*) FROM clients")
        total_clients = cursor.fetchone()[0]
        print(f"📊 Total de clientes no banco: {total_clients}")
        
        # Mostrar clientes sem categoria definida
        cursor.execute("SELECT COUNT(*) FROM clients WHERE category = 'Outros' OR category IS NULL")
        sem_categoria = cursor.fetchone()[0]
        print(f"⚠️  Clientes sem categoria específica: {sem_categoria}")
        
        conn.close()
        print("✅ Migração concluída com sucesso!")
        print("\n📋 Categorias disponíveis:")
        print("   - M.O - Matéria Prima")
        print("   - Comercial")
        print("   - Industrial")
        print("   - Serviços")
        print("   - Outros")
        print("\n💡 Use a interface admin para categorizar os clientes existentes.")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        return False

if __name__ == '__main__':
    if migrate():
        sys.exit(0)
    else:
        sys.exit(1)


