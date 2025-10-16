import sqlite3
import os

def test_database():
    db_path = 'database.db'
    
    if not os.path.exists(db_path):
        print("❌ Arquivo database.db não encontrado!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a tabela private_messages existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='private_messages'")
        private_messages_exists = cursor.fetchone() is not None
        print(f"✅ Tabela private_messages existe: {private_messages_exists}")
        
        # Verificar se a tabela notifications existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'")
        notifications_exists = cursor.fetchone() is not None
        print(f"✅ Tabela notifications existe: {notifications_exists}")
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"📋 Tabelas no banco: {[table[0] for table in tables]}")
        
        # Verificar estrutura da tabela private_messages se existir
        if private_messages_exists:
            cursor.execute("PRAGMA table_info(private_messages)")
            columns = cursor.fetchall()
            print(f"📊 Colunas da tabela private_messages:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao testar banco: {e}")

if __name__ == "__main__":
    test_database() 