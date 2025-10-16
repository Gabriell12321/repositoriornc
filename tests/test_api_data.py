import sqlite3

conn = sqlite3.connect('ippel_system.db')
cursor = conn.cursor()

# Testar dados mensais 2014
cursor.execute("""
    SELECT strftime('%m', finalized_at) as month, COUNT(*) as count 
    FROM rncs 
    WHERE finalized_at IS NOT NULL 
    AND strftime('%Y', finalized_at) = '2014' 
    GROUP BY month 
    ORDER BY month
""")
data_2014 = cursor.fetchall()
print('Dados mensais 2014:')
for month, count in data_2014:
    print(f'  Mês {month}: {count} RNCs')

# Testar dados por departamento 2014-2015 usando users.department
cursor.execute("""
    SELECT 
        u.department,
        COUNT(*) as count
    FROM rncs r
    JOIN users u ON r.user_id = u.id
    WHERE r.finalized_at IS NOT NULL 
    AND strftime('%Y', r.finalized_at) IN ('2014', '2015')
    AND u.department IS NOT NULL
    AND u.department != ''
    GROUP BY u.department
    ORDER BY count DESC
""")
dept_data = cursor.fetchall()
print('\nDados por departamento 2014-2015:')
for dept, count in dept_data:
    print(f'  {dept}: {count} RNCs')

conn.close()
