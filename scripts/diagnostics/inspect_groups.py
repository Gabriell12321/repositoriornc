import sqlite3

conn = sqlite3.connect('ippel_system.db')
c = conn.cursor()
print('=== USERS ENGENHARIA (id,name,department,group_id) ===')
for row in c.execute("SELECT id,name,department,group_id FROM users WHERE department='Engenharia' LIMIT 30"):
    print(row)
print('\n=== GROUPS (id,name) ===')
for row in c.execute("SELECT id,name FROM groups"):
    print(row)
print('\n=== Última RNC criada (id, rnc_number, department, user_id) ===')
for row in c.execute("SELECT id,rnc_number,department,user_id FROM rncs ORDER BY id DESC LIMIT 3"):
    print(row)
print('\n=== Compartilhamentos recentes (rnc_id, shared_with_user_id) ===')
for row in c.execute("SELECT rnc_id, shared_with_user_id FROM rnc_shares ORDER BY id DESC LIMIT 10"):
    print(row)
conn.close()
