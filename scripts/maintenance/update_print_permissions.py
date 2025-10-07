import sqlite3

# Connect to the database
conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# First check if permission exists for admin group (5)
cursor.execute("SELECT * FROM group_permissions WHERE permission_name = 'can_print_reports' AND group_id = 5")
result = cursor.fetchone()

if result is None:
    # Insert permission for admin group if it doesn't exist
    cursor.execute("INSERT INTO group_permissions (group_id, permission_name, permission_value) VALUES (5, 'can_print_reports', 1)")
    print("Added permission for admin group (5)")
else:
    # Update the permissions for groups 1 and 5
    cursor.execute("UPDATE group_permissions SET permission_value = 1 WHERE permission_name = 'can_print_reports' AND (group_id = 1 OR group_id = 5)")
    print("Updated permission for groups 1 and 5")

conn.commit()

# Confirm the update
cursor.execute("SELECT group_id, permission_name, permission_value FROM group_permissions WHERE permission_name = 'can_print_reports'")
results = cursor.fetchall()
print("Updated permissions:")
for row in results:
    print(f"Group {row[0]}: {'Enabled' if row[2] == 1 else 'Disabled'}")

# Close the connection
conn.close()
print("Database updated successfully")
