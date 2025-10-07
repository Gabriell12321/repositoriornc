import sqlite3

# Connect to the database
conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Check if admin user exists
cursor.execute("SELECT id, name, email, department FROM users WHERE email = 'admin@ippel.com.br'")
admin = cursor.fetchone()

if admin:
    # Update admin user department if it's not already set
    if not admin[3] or admin[3].lower() not in ['administração', 'administracao', 'ti', 'qualidade']:
        cursor.execute("UPDATE users SET department = 'Administração' WHERE id = ?", (admin[0],))
        print(f"Updated admin user (ID: {admin[0]}) with department 'Administração'")
    else:
        print(f"Admin user already has department: {admin[3]}")
else:
    print("Admin user not found")

# Ensure all users have a department
cursor.execute("SELECT id, name, email, department FROM users WHERE department IS NULL OR department = ''")
users = cursor.fetchall()

for user in users:
    cursor.execute("UPDATE users SET department = 'Geral' WHERE id = ?", (user[0],))
    print(f"Updated user {user[1]} (ID: {user[0]}) with default department 'Geral'")

# Commit changes
conn.commit()

# Verify all users now
cursor.execute("SELECT id, name, email, department FROM users")
all_users = cursor.fetchall()
print("\nAll users:")
for user in all_users:
    print(f"ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Department: {user[3]}")

conn.close()
print("\nDatabase updated successfully")
