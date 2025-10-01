import sqlite3

def check_users_structure():
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela users
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("Estrutura da tabela 'users':")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
            
        # Verificar alguns dados de usuários
        cursor.execute("SELECT id, name, department, email FROM users LIMIT 10")
        users = cursor.fetchall()
        
        print("\nExemplo de usuários:")
        for user in users:
            print(f"- ID: {user[0]}, Nome: {user[1]}, Departamento: {user[2]}, Email: {user[3]}")
            
        conn.close()
        
    except Exception as e:
        print(f"Erro ao verificar estrutura: {e}")

if __name__ == "__main__":
    check_users_structure()