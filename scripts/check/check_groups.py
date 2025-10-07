import sqlite3

# Conectar ao banco
conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Verificar se tabela groups existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='groups'")
groups_table_exists = bool(cursor.fetchone())
print(f"Tabela groups existe: {groups_table_exists}")

if groups_table_exists:
    # Verificar quantidade de grupos
    cursor.execute("SELECT COUNT(*) FROM groups")
    count = cursor.fetchone()[0]
    print(f"Total de grupos: {count}")
    
    # Listar alguns grupos
    cursor.execute("SELECT id, name, description FROM groups LIMIT 10")
    groups = cursor.fetchall()
    print("Grupos encontrados:")
    for group in groups:
        print(f"  ID: {group[0]}, Nome: {group[1]}, Descrição: {group[2]}")
else:
    print("Tabela groups não existe!")

conn.close()