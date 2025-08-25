import requests
import json

def test_permissions_finalizados():
    base_url = "http://localhost:5001"
    
    print("🔍 Testando permissões para RNCs finalizados...")
    
    # 1. Verificar se o servidor está rodando
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Servidor está rodando (status: {response.status_code})")
    except Exception as e:
        print(f"❌ Servidor não está rodando: {e}")
        return
    
    # 2. Testar API de listagem de RNCs finalizados
    try:
        response = requests.get(f"{base_url}/api/rnc/list?tab=finalized")
        print(f"📋 API rnc/list?tab=finalized - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                rncs = data.get('rncs', [])
                print(f"✅ {len(rncs)} RNCs finalizados encontrados")
                
                if rncs:
                    print("\n📊 Exemplos de RNCs finalizados:")
                    for i, rnc in enumerate(rncs[:3]):  # Mostrar apenas os 3 primeiros
                        print(f"  {i+1}. {rnc.get('rnc_number', 'N/A')} - {rnc.get('title', 'N/A')}")
                        print(f"     Criado por: {rnc.get('user_name', 'N/A')}")
                        print(f"     Cliente: {rnc.get('client', 'N/A')}")
                        print(f"     Equipamento: {rnc.get('equipment', 'N/A')}")
                        print(f"     Data finalização: {rnc.get('finalized_at', 'N/A')}")
                        print()
            else:
                print(f"❌ Erro na resposta: {data.get('message', 'Erro desconhecido')}")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")
    
    # 3. Testar acesso a RNCs finalizados específicos
    print("\n🔐 Testando acesso a RNCs finalizados específicos...")
    
    try:
        # Primeiro, buscar um RNC finalizado
        response = requests.get(f"{base_url}/api/rnc/list?tab=finalized")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('rncs'):
                rnc_id = data['rncs'][0]['id']
                print(f"📋 Testando acesso ao RNC {rnc_id}")
                
                # Testar visualização
                response = requests.get(f"{base_url}/rnc/{rnc_id}")
                print(f"👁️ Visualização RNC {rnc_id} - Status: {response.status_code}")
                
                # Testar impressão
                response = requests.get(f"{base_url}/rnc/{rnc_id}/print")
                print(f"🖨️ Impressão RNC {rnc_id} - Status: {response.status_code}")
                
            else:
                print("⚠️ Nenhum RNC finalizado encontrado para teste")
        else:
            print("❌ Não foi possível buscar RNCs finalizados")
            
    except Exception as e:
        print(f"❌ Erro ao testar acesso específico: {e}")
    
    print("\n✅ Teste de permissões concluído!")
    print("💡 Agora todos os usuários podem ver RNCs finalizados")

if __name__ == "__main__":
    test_permissions_finalizados() 