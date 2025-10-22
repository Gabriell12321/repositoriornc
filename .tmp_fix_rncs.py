import sqlite3, os, shutil, datetime
DB='ippel_system.db'
if not os.path.exists(DB):
    print('Database not found:', DB)
    raise SystemExit(1)
# Backup
ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
bak = f"{DB}.backup_{ts}"
shutil.copy2(DB, bak)
print('Backup created at', bak)

conn = sqlite3.connect(DB)
c = conn.cursor()

# Inspect users table columns
c.execute("PRAGMA table_info(users)")
user_cols = [r[1] for r in c.fetchall()]
print('users columns:', user_cols)

# Inspect rnc_shares columns
c.execute("PRAGMA table_info(rnc_shares)")
shares_cols = [r[1] for r in c.fetchall()]
print('rnc_shares columns:', shares_cols)

# Helper: get active users for a group id
def get_group_users(gid):
    users = []
    # Prefer column 'group_id'
    if 'group_id' in user_cols:
        if 'is_active' in user_cols:
            c.execute('SELECT id FROM users WHERE group_id=? AND is_active=1', (gid,))
        elif 'active' in user_cols:
            c.execute('SELECT id FROM users WHERE group_id=? AND active=1', (gid,))
        else:
            c.execute('SELECT id FROM users WHERE group_id=?', (gid,))
        users = [r[0] for r in c.fetchall()]
    else:
        # Fallback: try users with groups stored in group_ids JSON/text (rare)
        try:
            c.execute("SELECT id, group_ids FROM users WHERE group_ids IS NOT NULL")
            for uid, gstr in c.fetchall():
                try:
                    if isinstance(gstr, str) and str(gid) in gstr:
                        users.append(uid)
                except Exception:
                    pass
        except Exception:
            pass
    return users

updated_rncs = []
shares_inserted = 0

# Get rncs that likely need assigned_group_id (area_responsavel not empty and assigned_group_id IS NULL)
c.execute("SELECT id, area_responsavel, user_id FROM rncs WHERE assigned_group_id IS NULL AND COALESCE(TRIM(area_responsavel),'')<>''")
rows = c.fetchall()
print('Candidate RNCs for assignment resolution:', len(rows))

for r in rows:
    rnc_id, area_raw, creator = r
    assigned = None
    # Try numeric
    try:
        if area_raw and area_raw.strip().isdigit():
            assigned = int(area_raw.strip())
    except Exception:
        assigned = None
    # Try exact name
    if not assigned:
        try:
            name = area_raw.strip()
            if name:
                c.execute('SELECT id FROM groups WHERE lower(name)=lower(?) LIMIT 1', (name,))
                row = c.fetchone()
                if row:
                    assigned = int(row[0])
        except Exception:
            assigned = None
    # Try LIKE fallback
    if not assigned:
        try:
            name = area_raw.strip()
            if name:
                c.execute('SELECT id FROM groups WHERE lower(name) LIKE lower(?) LIMIT 1', (f"%{name}%",))
                row = c.fetchone()
                if row:
                    assigned = int(row[0])
        except Exception:
            assigned = None
    # Apply update if found
    if assigned:
        try:
            c.execute('UPDATE rncs SET assigned_group_id=? WHERE id=?', (assigned, rnc_id))
            updated_rncs.append((rnc_id, assigned, creator))
            print(f'Updated rnc {rnc_id} -> assigned_group_id={assigned}')
        except Exception as e:
            print('Error updating rnc', rnc_id, e)

conn.commit()
print('Total rncs updated with assigned_group_id:', len(updated_rncs))

# For each updated rnc, insert shares for users in that group
for rnc_id, assigned_group, creator in updated_rncs:
    users = get_group_users(assigned_group)
    print(f' - rnc {rnc_id} group {assigned_group} users found: {len(users)}')
    for uid in users:
        if uid == creator:
            continue
        # Check existing share
        try:
            c.execute('SELECT 1 FROM rnc_shares WHERE rnc_id=? AND shared_with_user_id=?', (rnc_id, uid))
            if c.fetchone():
                continue
            # Build insert based on available columns
            if all(col in shares_cols for col in ['rnc_id','shared_by_user_id','shared_with_user_id','permission_level']):
                c.execute("INSERT INTO rnc_shares (rnc_id, shared_by_user_id, shared_with_user_id, permission_level) VALUES (?,?,?,?)", (rnc_id, creator, uid, 'assigned'))
                shares_inserted += 1
            elif all(col in shares_cols for col in ['rnc_id','shared_with_user_id']):
                c.execute("INSERT INTO rnc_shares (rnc_id, shared_with_user_id) VALUES (?,?)", (rnc_id, uid))
                shares_inserted += 1
            else:
                print('Unknown rnc_shares schema; skip inserting for now')
        except Exception as e:
            print('Error inserting share for rnc', rnc_id, 'user', uid, e)

conn.commit()
print('Total shares inserted:', shares_inserted)
conn.close()
print('Done')
