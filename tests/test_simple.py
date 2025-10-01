import requests

s = requests.Session()
try:
    # Login
    response = s.post('http://192.168.3.11:5001/login', data={
        'email': 'admin@exemplo.com', 
        'password': 'admin123'
    })
    print(f'Login status: {response.status_code}')
    
    if response.status_code == 200:
        # Listar RNCs finalizadas
        response = s.get('http://192.168.3.11:5001/list_rncs?tab=finalized')
        print(f'List RNCs status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            if 'rncs' in data and len(data['rncs']) > 0:
                rnc = data['rncs'][0]
                print(f"RNC {rnc.get('rnc_number', 'N/A')}")
                print(f"  Setor: {rnc.get('setor', 'N/A')}")
                print(f"  Department: {rnc.get('department', 'N/A')}")
                print(f"  User Department: {rnc.get('user_department', 'N/A')}")
            else:
                print('Nenhuma RNC encontrada')
        else:
            print(f'Erro na list_rncs: {response.status_code}')
    else:
        print(f'Erro no login: {response.status_code}')
        
except Exception as e:
    print(f'Erro: {e}')
