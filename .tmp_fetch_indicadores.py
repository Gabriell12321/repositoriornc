import requests, json
urls=['http://127.0.0.1:5000/api/indicadores/engenharia','http://127.0.0.1:5000/api/indicadores','http://127.0.0.1:5000/api/indicadores/setor?setor=engenharia']
for u in urls:
    try:
        r = requests.get(u, timeout=5)
        print('URL:',u,' status=',r.status_code)
        try:
            j=r.json()
            print(' keys:', list(j.keys())[:10])
        except Exception as e:
            print(' json parse err', e)
    except Exception as e:
        print('request failed',u,e)
