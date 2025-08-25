import requests
import json

def test_dashboard_api():
    base_url = "http://localhost:5001"
    
    print("🔍 Testando API do Dashboard...")
    
    # 1. Testar se o servidor está rodando
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Servidor está rodando (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Servidor não está rodando: {e}")
        return
    
    # 2. Testar API de informações do usuário
    try:
        response = requests.get(f"{base_url}/api/user/info")
        print(f"📊 API user/info - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Informações do usuário: {data.get('user', {}).get('name', 'N/A')}")
        else:
            print(f"❌ Erro na API user/info: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao testar API user/info: {e}")
    
    # 3. Testar API de listagem de RNCs (lixeira removida)
    tabs = ['active', 'finalized']
    
    for tab in tabs:
        try:
            response = requests.get(f"{base_url}/api/rnc/list?tab={tab}")
            print(f"📋 API rnc/list?tab={tab} - Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    rncs = data.get('rncs', [])
                    print(f"✅ {tab.upper()}: {len(rncs)} RNCs encontrados")
                    
                    if rncs:
                        print(f"   Exemplo: {rncs[0].get('rnc_number', 'N/A')} - {rncs[0].get('title', 'N/A')}")
                else:
                    print(f"❌ Erro na resposta: {data.get('message', 'Erro desconhecido')}")
            else:
                print(f"❌ Erro HTTP: {response.text}")
                
        except Exception as e:
            print(f"❌ Erro ao testar API rnc/list?tab={tab}: {e}")
    
    # 4. Testar se há problemas de CORS ou autenticação
    print("\n🔐 Verificando problemas de autenticação...")
    
    try:
        # Testar sem sessão
        response = requests.get(f"{base_url}/api/rnc/list?tab=active")
        if response.status_code == 401:
            print("⚠️ API requer autenticação (normal)")
        elif response.status_code == 200:
            print("✅ API não requer autenticação")
        else:
            print(f"⚠️ Status inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar autenticação: {e}")
    
    print("\n💡 Para testar completamente, faça login no sistema primeiro")

if __name__ == "__main__":
    test_dashboard_api() 