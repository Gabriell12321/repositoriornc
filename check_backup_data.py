import sqlite3
import os
from datetime import datetime

# Listar todos os backups
backups = [f for f in os.listdir('.') if f.startswith('ippel_system_backup_') and f.endswith('.db')]
backups.sort(reverse=True)

print("=== Verificando RNCs nos backups ===\n")

for backup in backups[:5]:  # Verificar os 5 mais recentes
    try:
        conn = sqlite3.connect(backup)
        cursor = conn.cursor()
        
        # Verificar se a tabela existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rncs'")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM rncs WHERE (is_deleted = 0 OR is_deleted IS NULL)")
            count = cursor.fetchone()[0]
            
            # Pegar timestamp do arquivo
            mtime = os.path.getmtime(backup)
            timestamp = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"📁 {backup}")
            print(f"   Data: {timestamp}")
            print(f"   RNCs: {count}")
            
            if count > 0:
                cursor.execute("SELECT COUNT(*) FROM rncs WHERE finalized_at IS NOT NULL AND (is_deleted = 0 OR is_deleted IS NULL)")
                finalized = cursor.fetchone()[0]
                print(f"   Finalizadas: {finalized}")
                print(f"   ✅ ESTE BACKUP TEM DADOS!")
            print()
        
        conn.close()
    except Exception as e:
        print(f"❌ Erro ao verificar {backup}: {e}\n")

print("\n=== Banco atual ===")
try:
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM rncs WHERE (is_deleted = 0 OR is_deleted IS NULL)")
    count = cursor.fetchone()[0]
    print(f"RNCs no banco atual: {count}")
    conn.close()
except Exception as e:
    print(f"Erro: {e}")
