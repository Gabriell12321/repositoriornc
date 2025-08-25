import sqlite3

def check_tables():
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("Tabelas no banco:")
        for table in tables:
            print(f"- {table[0]}")
            
            # Contar registros em cada tabela
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"  Registros: {count}")
            except Exception as e:
                print(f"  Erro ao contar: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro ao verificar banco: {e}")

if __name__ == "__main__":
    check_tables()