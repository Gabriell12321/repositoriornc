import sqlite3

def check_rncs_structure():
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela rncs
        cursor.execute("PRAGMA table_info(rncs)")
        columns = cursor.fetchall()
        
        print("Estrutura da tabela 'rncs':")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
            
        conn.close()
        
    except Exception as e:
        print(f"Erro ao verificar estrutura: {e}")

if __name__ == "__main__":
    check_rncs_structure()