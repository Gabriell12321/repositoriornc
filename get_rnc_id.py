import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

cursor.execute('SELECT id FROM rncs WHERE rnc_number = ?', ('RNC-2025-08-28-102946',))
result = cursor.fetchone()

if result:
    print(f"ID da RNC: {result[0]}")
    print(f"URL: http://localhost:5000/rnc/{result[0]}")
else:
    print("RNC não encontrada")

conn.close()
