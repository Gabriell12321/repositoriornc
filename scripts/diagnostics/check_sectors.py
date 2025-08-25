import sqlite3

def check_sectors():
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela sectors
        cursor.execute("PRAGMA table_info(sectors)")
        columns = cursor.fetchall()
        
        print("Estrutura da tabela 'sectors':")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
            
        # Verificar dados na tabela sectors
        cursor.execute("SELECT * FROM sectors")
        sectors = cursor.fetchall()
        
        print("\nDados na tabela 'sectors':")
        for sector in sectors:
            print(f"- {sector}")
            
        conn.close()
        
    except Exception as e:
        print(f"Erro ao verificar setores: {e}")

if __name__ == "__main__":
    check_sectors()