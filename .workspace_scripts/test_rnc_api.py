import sys, json, os
sys.path.insert(0, r'C:\Programação\repositoriornc-d25fe14acd0148664f67c4d9940f057b894cd479')

from server_form import app

queries = [
    ('finalized_year_2024', '/api/rnc/list?tab=finalized&year=2024'),
    ('finalized_year_2023', '/api/rnc/list?tab=finalized&year=2023'),
    ('finalized_status_Finalizado', '/api/rnc/list?tab=finalized&status=Finalizado'),
    ('finalized_date_range', '/api/rnc/list?tab=finalized&date_start=2024-01-01&date_end=2024-12-31'),
]

print('Starting Flask test client against in-process app')
with app.test_client() as c:
    # set a session user (assume user id 1 exists and has permissions)
    with c.session_transaction() as sess:
        sess['user_id'] = 1

    for name, path in queries:
        try:
            rv = c.get(path)
            status = rv.status_code
            try:
                data = rv.get_json()
            except Exception:
                data = None
            rncs_count = len(data.get('rncs', [])) if isinstance(data, dict) and 'rncs' in data else 'no-json'
            sample = None
            if isinstance(data, dict) and 'rncs' in data and len(data['rncs'])>0:
                sample = data['rncs'][0]
            print('---')
            print('query:', name)
            print('path:', path)
            print('status:', status)
            print('rncs_count:', rncs_count)
            if sample:
                # print a few useful fields
                print('sample_id:', sample.get('id'))
                print('sample_rnc_number:', sample.get('rnc_number'))
                print('sample_finalized_at:', sample.get('finalized_at'))
                print('sample_status:', sample.get('status'))
        except Exception as e:
            print('ERROR calling', path, e)

print('Done')
