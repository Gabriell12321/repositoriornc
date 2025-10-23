import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()
cursor.execute('''
    SELECT r.*,
           u.name as user_name,
           au.name as assigned_user_name,
           u.department as user_department,
           au.department as assigned_user_department,
           g.name as area_responsavel_name,
           resp_user.name as responsavel_name,
           insp_user.name as inspetor_name
    FROM rncs r
    LEFT JOIN users u ON r.user_id = u.id
    LEFT JOIN users au ON r.assigned_user_id = au.id
    LEFT JOIN groups g ON g.id = CAST(r.area_responsavel AS INTEGER)
    LEFT JOIN users resp_user ON resp_user.id = CAST(r.responsavel AS INTEGER)
    LEFT JOIN users insp_user ON insp_user.id = CAST(r.inspetor AS INTEGER)
    WHERE r.id = 14856
''')
row = cursor.fetchone()
cols = [desc[0] for desc in cursor.description]

print(f'Total colunas: {len(row)}')
print(f'Total descrição: {len(cols)}')
print(f'\nÍndice area_responsavel_name: {cols.index("area_responsavel_name")}')
print(f'Valor: {row[cols.index("area_responsavel_name")]}')
print(f'\nÍndice responsavel_name: {cols.index("responsavel_name")}')
print(f'Valor: {row[cols.index("responsavel_name")]}')
print(f'\nÍndice inspetor_name: {cols.index("inspetor_name")}')
print(f'Valor: {row[cols.index("inspetor_name")]}')

conn.close()
