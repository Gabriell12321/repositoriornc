import sqlite3

# Conectar ao banco
conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Verificar usuarios
cursor.execute("SELECT id, email, role FROM users WHERE role = 'admin'")
admins = cursor.fetchall()
print("Usuários admin encontrados:")
for admin in admins:
    print(f"  ID: {admin[0]}, Email: {admin[1]}, Role: {admin[2]}")

conn.close()