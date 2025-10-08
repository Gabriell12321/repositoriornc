import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

print("=== Análise Detalhada das RNCs ===\n")

# User IDs
cursor.execute("SELECT user_id, COUNT(*) FROM rncs GROUP BY user_id")
print("Por User ID:")
for row in cursor.fetchall():
    print(f"  User {row[0]}: {row[1]} RNCs")

# is_deleted
cursor.execute("SELECT is_deleted, COUNT(*) FROM rncs GROUP BY is_deleted")
print("\nPor is_deleted:")
for row in cursor.fetchall():
    deleted = "SIM" if row[0] == 1 else "NÃO" if row[0] == 0 else "NULL"
    print(f"  {deleted}: {row[1]} RNCs")

# Status completo
cursor.execute("SELECT status, COUNT(*) FROM rncs GROUP BY status ORDER BY COUNT(*) DESC")
print("\nStatus:")
for row in cursor.fetchall():
    print(f"  '{row[0]}': {row[1]} RNCs")

# Verificar permissões do usuário 1
cursor.execute("SELECT id, name, email, role FROM users WHERE id = 1")
user = cursor.fetchone()
if user:
    print(f"\nUsuário Admin:")
    print(f"  ID: {user[0]}")
    print(f"  Nome: {user[1]}")
    print(f"  Email: {user[2]}")
    print(f"  Role: {user[3]}")

# Amostra de RNCs
print("\n=== Primeiras 3 RNCs ===")
cursor.execute("SELECT id, rnc_number, title, status, user_id, is_deleted FROM rncs LIMIT 3")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, RNC: {row[1]}, Status: {row[3]}, User: {row[4]}, Deleted: {row[5]}")

conn.close()
