import sys, os
sys.path.insert(0, r'C:\Programação\repositoriornc-d25fe14acd0148664f67c4d9940f057b894cd479')
from server_form import app

with app.test_client() as c:
    with c.session_transaction() as sess:
        sess['user_id'] = 1
    rv = c.get('/dashboard')
    print('STATUS', rv.status_code)
    html = rv.get_data(as_text=True)
    out = os.path.join(os.getcwd(), 'tmp_dashboard_authenticated.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print('Saved to', out)
    keys = ['filterYear','filterStatus','RNCs Mensais por Setor','buildSetorCharts','applySetorFilters']
    for k in keys:
        print(k, '=>', k in html)
    # print a small snippet where filters might live
    idx = html.find('filtersContainer')
    if idx!=-1:
        print('filtersContainer snippet:', html[idx:idx+400])
    else:
        print('filtersContainer not found')
