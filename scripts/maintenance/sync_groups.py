import sqlite3

conn = sqlite3.connect('ippel_system.db')
c = conn.cursor()

# Map group name -> id
c.execute('SELECT id,name FROM groups')
name_to_id = {name:id_ for id_,name in c.fetchall()}

# Atribuir group_id onde está NULL mas department coincide
updated = 0
for name,id_ in name_to_id.items():
    c.execute('UPDATE users SET group_id = ? WHERE group_id IS NULL AND department = ?', (id_, name))
    updated += c.rowcount

conn.commit()
print(f'Atribuídos group_id para {updated} usuários.')

# Preencher department vazio nas últimas 20 RNCs usando departamento do criador
c.execute("SELECT id,user_id FROM rncs WHERE (department IS NULL OR department='') ORDER BY id DESC LIMIT 50")
fix_targets = c.fetchall()
filled = 0
for rnc_id,uid in fix_targets:
    c.execute('SELECT department FROM users WHERE id=?', (uid,))
    dep = c.fetchone()
    if dep and dep[0]:
        c.execute('UPDATE rncs SET department=? WHERE id=?', (dep[0], rnc_id))
        filled += 1
conn.commit()
print(f'Atualizadas {filled} RNCs com department do criador.')

# Criar compartilhamentos faltantes (baseado em department)
created_shares = 0
for rnc_id,uid in fix_targets:
    c.execute('SELECT department FROM rncs WHERE id=?', (rnc_id,))
    dep_row = c.fetchone()
    if not dep_row or not dep_row[0]:
        continue
    dep = dep_row[0]
    # usuários do mesmo department (excluir criador)
    c.execute('SELECT id FROM users WHERE department=? AND id != ? AND is_active=1', (dep, uid))
    for (target_id,) in c.fetchall():
        c.execute('INSERT OR IGNORE INTO rnc_shares (rnc_id, shared_by_user_id, shared_with_user_id, permission_level) VALUES (?,?,?,"view")', (rnc_id, uid, target_id))
        created_shares += c.rowcount
conn.commit()
print(f'Criados {created_shares} compartilhamentos retroativos.')

conn.close()
print('Sincronização concluída.')
