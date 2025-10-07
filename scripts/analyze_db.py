import sqlite3

def analyze_database():
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Listar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("=== TABELAS DO BANCO ===")
        for table in tables:
            print(f"  - {table[0]}")
            
        # Analisar estrutura da tabela RNCs
        print("\n=== ESTRUTURA DA TABELA RNCs ===")
        cursor.execute("PRAGMA table_info(rncs);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
            
        # Contar registros
        print("\n=== CONTAGEM DE REGISTROS ===")
        cursor.execute("SELECT COUNT(*) FROM rncs;")
        total_rncs = cursor.fetchone()[0]
        print(f"Total de RNCs: {total_rncs}")
        
        cursor.execute("SELECT COUNT(*) FROM users;")
        total_users = cursor.fetchone()[0]
        print(f"Total de usuários: {total_users}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    analyze_database()
