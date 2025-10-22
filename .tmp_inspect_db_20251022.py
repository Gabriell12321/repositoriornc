import sqlite3, json, sys
DB='ippel_system.db'
conn=sqlite3.connect(DB)
cur=conn.cursor()
out={}
try:
    cur.execute("SELECT COALESCE(strftime('%Y', finalized_at), strftime('%Y', created_at)) as year, status, COUNT(*) FROM rncs GROUP BY year, status ORDER BY year DESC")
    rows=cur.fetchall()
    gby={}
    for year,status,cnt in rows:
        y=year or 'unknown'
        gby.setdefault(y,{})
        gby[y][status or 'unknown']=cnt
    out['global_by_year']=gby

    cur.execute("SELECT COALESCE(strftime('%Y', finalized_at), strftime('%Y', created_at)) as year, COUNT(*) FROM rncs WHERE status='Finalizado' GROUP BY year ORDER BY year DESC")
    out['finalized_by_year']=dict(cur.fetchall())

    cur.execute("SELECT id, rnc_number, title, status, finalized_at, assigned_group_id, assigned_user_id, user_id FROM rncs WHERE COALESCE(strftime('%Y', finalized_at), strftime('%Y', created_at)) = '2024' ORDER BY id DESC LIMIT 200")
    rows=cur.fetchall()
    out['sample_2024_count']=len(rows)
    out['sample_2024']=[]
    ids=[]
    for r in rows:
        ids.append(str(r[0]))
        out['sample_2024'].append({
            'id': r[0], 'rnc_number': r[1], 'title': (r[2] or '')[:120], 'status': r[3], 'finalized_at': r[4], 'assigned_group_id': r[5], 'assigned_user_id': r[6], 'user_id': r[7]
        })

    shares={}
    if ids:
        q=f"SELECT rnc_id, shared_with_user_id, shared_by_user_id, permission_level FROM rnc_shares WHERE rnc_id IN ({','.join(ids)})"
        try:
            cur.execute(q)
            srows=cur.fetchall()
            for r in srows:
                shares.setdefault(r[0],[]).append({'shared_with_user_id':r[1],'shared_by_user_id':r[2],'permission_level':r[3]})
        except Exception as e:
            shares['error']=str(e)
    out['rnc_shares_sample']=shares

    print(json.dumps(out, ensure_ascii=False, indent=2))
except Exception as e:
    print('Error:', e, file=sys.stderr)
finally:
    conn.close()
