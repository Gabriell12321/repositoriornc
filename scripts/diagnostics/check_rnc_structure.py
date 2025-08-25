import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Verificar se existe sector_id na tabela rncs
cursor.execute("PRAGMA table_info(rncs)")
columns = cursor.fetchall()
print('Colunas da tabela rncs que contêm "sector" ou relacionadas:')
for col in columns:
    if 'sector' in col[1].lower() or 'department' in col[1].lower() or 'area' in col[1].lower():
        print(f'  {col[1]} ({col[2]})')

# Verificar um RNC de exemplo
cursor.execute("SELECT * FROM rncs WHERE finalized_at IS NOT NULL LIMIT 1")
row = cursor.fetchone()
if row:
    col_names = [desc[0] for desc in cursor.description]
    print('\nExemplo de RNC finalizado:')
    for i, col_name in enumerate(col_names):
        if row[i] is not None:
            print(f'  {col_name}: {row[i]}')

# Verificar se existe relação através de user_id
cursor.execute("""
    SELECT DISTINCT u.id, u.username 
    FROM users u
    JOIN rncs r ON r.user_id = u.id
    WHERE r.finalized_at IS NOT NULL
    LIMIT 10
""")
users = cursor.fetchall()
print('\nUsuários que criaram RNCs finalizados:')
for user in users:
    print(f'  ID: {user[0]}, Nome: {user[1]}')

conn.close()
