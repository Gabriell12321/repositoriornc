import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(rncs)')
columns = [col[1] for col in cursor.fetchall()]

print("🔍 Verificando campos relacionados:")
print("Campos que contêm 'instruction':", [c for c in columns if 'instruction' in c.lower()])
print("Campos que contêm 'cause':", [c for c in columns if 'cause' in c.lower()])
print("Campos que contêm 'action':", [c for c in columns if 'action' in c.lower()])
print("Campos que contêm 'retrabalho':", [c for c in columns if 'retrabalho' in c.lower()])

conn.close()
