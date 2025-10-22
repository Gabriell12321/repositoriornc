import sys, os
sys.path.insert(0, r'C:\Programação\repositoriornc-d25fe14acd0148664f67c4d9940f057b894cd479')
from server_form import app

paths = ['/', '/dashboard', '/dashboard_improved', '/dashboard_improved.html', '/dashboard/improved']
found = False
with app.test_client() as c:
    for p in paths:
        try:
            rv = c.get(p)
            print('PATH', p, 'STATUS', rv.status_code)
            if rv.status_code == 200:
                html = rv.get_data(as_text=True)
                snippet = html[:800]
                print('SNIPPET:\n', snippet)
                # Save to file
                out = os.path.join(os.getcwd(), 'tmp_dashboard.html')
                with open(out, 'w', encoding='utf-8') as f:
                    f.write(html)
                print('Saved to', out)
                # Check for keywords
                for key in ('filterYear','filterStatus','RNCs Mensais por Setor','buildSetorCharts'):
                    print(key, '=>', key in html)
                found = True
                break
        except Exception as e:
            print('ERR', p, e)
if not found:
    print('No dashboard route returned 200 from tried paths')
