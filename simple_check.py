import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM users')
print('Total usuários:', cursor.fetchone()[0])

cursor.execute('SELECT id, name FROM users ORDER BY id DESC LIMIT 10')
print('Últimos usuários criados:')
for row in cursor.fetchall():
    print(f'ID {row[0]}: {row[1]}')

conn.close()
