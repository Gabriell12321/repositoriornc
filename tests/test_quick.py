import requests
import json

# Login
login_data = {'email': 'admin@exemplo.com', 'password': 'admin123'}
s = requests.Session()
login_response = s.post('http://localhost:5001/login', data=login_data)

if login_response.status_code == 200:
    print('✅ Login realizado')
    # Fazer requisição para RNCs finalizadas
    response = s.get('http://localhost:5001/list_rncs?tab=finalized')
    if response.status_code == 200:
        data = response.json()
        if 'rncs' in data and len(data['rncs']) > 0:
            rnc = data['rncs'][0]
            print(f'RNC {rnc.get("rnc_number")}: Setor = {rnc.get("setor")}, Department = {rnc.get("department")}')
            print(f'User Department = {rnc.get("user_department")}')
        else:
            print('Nenhuma RNC encontrada')
    else:
        print(f'Erro na requisição: {response.status_code}')
else:
    print(f'Erro no login: {login_response.status_code}')
