#!/usr/bin/env python3
"""
Script para fazer checkpoint do WAL e aplicar migração
"""

import sqlite3
import os

DB_PATH = 'ippel_system.db'

def checkpoint_wal():
    """Faz checkpoint do WAL para integrar mudanças no arquivo principal"""
    try:
        print("🔄 Fazendo checkpoint do WAL...")
        conn = sqlite3.connect(DB_PATH)
        conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        conn.close()
        print("✅ Checkpoint concluído!")
        return True
    except Exception as e:
        print(f"❌ Erro no checkpoint: {e}")
        return False

if __name__ == "__main__":
    checkpoint_wal()
