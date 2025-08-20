import requests
import json

def test_server():
    try:
        print("🧪 Testando conexão com servidor...")
        response = requests.get('http://127.0.0.1:5001/api/test', timeout=10)
        print(f"✅ Status: {response.status_code}")
        print(f"📦 Response: {response.text}")
        
        print("\n🔧 Testando endpoint engenharia...")
        eng_response = requests.get('http://127.0.0.1:5001/api/indicadores/engenharia', timeout=10)
        print(f"✅ Status: {eng_response.status_code}")
        print(f"📦 Response: {eng_response.text}")
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Erro de conexão: {e}")
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout: {e}")
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    test_server()
