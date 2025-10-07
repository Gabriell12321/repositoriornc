import sqlite3

conn = sqlite3.connect('ippel_system.db')
cur = conn.cursor()
print('Tabelas:')
for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    print(' -', r[0])
print('\nColunas rncs:')
for c in cur.execute('PRAGMA table_info(rncs)'):
    print(c)
print('\nTop 15 clientes:')
for row in cur.execute("SELECT client, COUNT(*) c FROM rncs WHERE client IS NOT NULL AND TRIM(client)!='' GROUP BY client ORDER BY c DESC LIMIT 15"):
    print(row)
conn.close()
