import requests
import json

def test_field_locks_server():
    try:
        print("🔍 Testando servidor na porta 5001...")
        
        # Testar API de grupos
        response = requests.get('http://localhost:5001/admin/field-locks/api/groups', timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            try:
                groups = response.json()
                print(f"✅ Grupos (parsed): {groups}")
                print(f"📊 Tipo: {type(groups)}")
                print(f"📊 Quantidade: {len(groups) if isinstance(groups, list) else 'N/A'}")
            except Exception as e:
                print(f"❌ Erro ao fazer parse JSON: {e}")
        else:
            print(f"❌ Status não é 200: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

if __name__ == "__main__":
    test_field_locks_server()