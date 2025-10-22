import sqlite3, os, json
DB='ippel_system.db'
if not os.path.exists(DB):
    print('Database file not found:', DB)
    raise SystemExit(1)
conn=sqlite3.connect(DB)
c=conn.cursor()

# Recent 50
c.execute('''SELECT id, rnc_number, area_responsavel, assigned_group_id, status, created_at, user_id FROM rncs ORDER BY created_at DESC LIMIT 50''')
rows=c.fetchall()
print('Found', len(rows), 'recent rncs')

for r in rows:
    rnc_id=r[0]
    c.execute('SELECT COUNT(*) FROM rnc_shares WHERE rnc_id=?', (rnc_id,))
    shares_count=c.fetchone()[0]
    print('RNC', r[1], 'id', rnc_id, 'area_responsavel=', r[2], 'assigned_group_id=', r[3], 'status=', r[4], 'shares=', shares_count)

# Show group 'Engenharia' id
c.execute("SELECT id FROM groups WHERE lower(name) LIKE '%engenharia%' COLLATE NOCASE LIMIT 1")
g=c.fetchone()
print('Engenharia group id:', g[0] if g else 'NOT FOUND')

# List RNCs assigned to Engenharia (assigned_group_id)
eng_id = g[0] if g else None
if eng_id:
    c.execute('SELECT id, rnc_number, area_responsavel, assigned_group_id, status, created_at FROM rncs WHERE assigned_group_id=? ORDER BY created_at DESC LIMIT 50', (eng_id,))
    erows=c.fetchall()
    print('\nRNCs with assigned_group_id = Engenharia (count):', len(erows))
    for r in erows:
        c.execute('SELECT COUNT(*) FROM rnc_shares WHERE rnc_id=?', (r[0],))
        shares=c.fetchone()[0]
        print(' -', r[1], 'id', r[0], 'area_responsavel=', r[2], 'shares=', shares, 'status=', r[4])

conn.close()
