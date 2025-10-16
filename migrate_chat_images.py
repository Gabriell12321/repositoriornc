#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migração: Adicionar suporte para imagens e arquivos no chat
Adiciona coluna 'file_path' na tabela 'chat_messages'
"""

import sqlite3
import os
from datetime import datetime

import sqlite3
import os
from datetime import datetime

# Caminho do banco de dados
DB_PATH = 'ippel_system.db'

def migrate_chat_images():
    """Adiciona coluna file_path à tabela chat_messages"""
    print("🔄 Iniciando migração para suporte a imagens no chat...")
    
    # Backup do banco
    backup_path = f'rnc_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    print(f"📦 Criando backup em: {backup_path}")
    
    import shutil
    shutil.copy2(DB_PATH, backup_path)
    print("✅ Backup criado com sucesso!")
    
    # Conectar ao banco
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(chat_messages)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'file_path' in columns:
            print("⚠️ Coluna 'file_path' já existe na tabela 'chat_messages'")
            return
        
        # Adicionar coluna file_path
        print("➕ Adicionando coluna 'file_path' à tabela 'chat_messages'...")
        cursor.execute('''
            ALTER TABLE chat_messages 
            ADD COLUMN file_path TEXT
        ''')
        
        conn.commit()
        print("✅ Coluna 'file_path' adicionada com sucesso!")
        
        # Criar pastas de upload
        print("📁 Criando pastas de upload...")
        os.makedirs('static/uploads/chat_images', exist_ok=True)
        os.makedirs('static/uploads/chat_files', exist_ok=True)
        print("✅ Pastas criadas!")
        
        # Verificar estrutura final
        print("\n📊 Estrutura da tabela 'chat_messages':")
        cursor.execute("PRAGMA table_info(chat_messages)")
        for col in cursor.fetchall():
            print(f"  - {col[1]} ({col[2]})")
        
        print("\n✅ Migração concluída com sucesso!")
        print(f"💾 Backup salvo em: {backup_path}")
        
    except Exception as e:
        print(f"❌ Erro durante migração: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_chat_images()
