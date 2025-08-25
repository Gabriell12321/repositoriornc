import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Ver tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print('Tabelas:')
for table in sorted(tables):
    print(f'  {table}')

# Ver estrutura da tabela rncs
cursor.execute("PRAGMA table_info(rncs)")
columns = cursor.fetchall()
print('\nColunas da tabela rncs:')
for col in columns:
    print(f'  {col[1]} ({col[2]})')

conn.close()
