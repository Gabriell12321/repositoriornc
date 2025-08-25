import requests
import json
import sqlite3
import os

def test_chat_system():
    base_url = "http://localhost:5001"
    
    print("🔍 Testando sistema de chat...")
    
    # 1. Verificar se o servidor está rodando
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Servidor está rodando (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Servidor não está rodando: {e}")
        return
    
    # 2. Verificar banco de dados
    db_path = 'database.db'
    if not os.path.exists(db_path):
        print("❌ Arquivo database.db não encontrado!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tabelas necessárias
        tables = ['users', 'private_messages', 'notifications']
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            exists = cursor.fetchone() is not None
            print(f"📋 Tabela {table}: {'✅ Existe' if exists else '❌ Não existe'}")
        
        # Verificar se há usuários
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        user_count = cursor.fetchone()[0]
        print(f"👥 Usuários ativos: {user_count}")
        
        # Verificar estrutura da tabela private_messages
        cursor.execute("PRAGMA table_info(private_messages)")
        columns = cursor.fetchall()
        print(f"📊 Colunas da tabela private_messages:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
    
    # 3. Testar login (se houver usuários)
    if user_count > 0:
        try:
            # Tentar fazer login com o primeiro usuário
            cursor.execute("SELECT email FROM users WHERE is_active = 1 LIMIT 1")
            user_email = cursor.fetchone()
            if user_email:
                print(f"🔐 Testando login com: {user_email[0]}")
                # Aqui você pode adicionar um teste de login se necessário
        except Exception as e:
            print(f"❌ Erro ao testar login: {e}")

if __name__ == "__main__":
    test_chat_system() 