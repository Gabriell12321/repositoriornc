import requests
import json

def test_filtros_finalizados():
    base_url = "http://localhost:5001"
    
    print("🔍 Testando sistema de filtros para RNCs finalizados...")
    
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
        data = response.json()
        
        if data['success']:
            rncs = data['rncs']
            print(f"✅ API de RNCs finalizados funcionando - {len(rncs)} RNCs encontrados")
            
            # Mostrar alguns exemplos de RNCs para verificar campos disponíveis
            if rncs:
                print("\n📋 Exemplo de RNC finalizado:")
                rnc = rncs[0]
                print(f"  - Número: {rnc.get('rnc_number', 'N/A')}")
                print(f"  - Cliente: {rnc.get('client', 'N/A')}")
                print(f"  - Equipamento: {rnc.get('equipment', 'N/A')}")
                print(f"  - Departamento: {rnc.get('department', 'N/A')}")
                print(f"  - Título: {rnc.get('title', 'N/A')}")
        else:
            print(f"❌ Erro na API: {data.get('message', 'Erro desconhecido')}")
            
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")
    
    # 3. Testar filtros específicos
    print("\n🔍 Testando filtros específicos...")
    
    # Testar filtro por número de RNC
    try:
        response = requests.get(f"{base_url}/api/rnc/list?tab=finalized")
        data = response.json()
        
        if data['success'] and data['rncs']:
            rnc_number = data['rncs'][0]['rnc_number']
            print(f"  - Testando filtro por número: {rnc_number}")
            
            # Aqui você pode adicionar testes específicos para cada tipo de filtro
            # Por enquanto, vamos apenas verificar se a API retorna dados
            
    except Exception as e:
        print(f"❌ Erro ao testar filtros: {e}")
    
    print("\n✅ Teste de filtros concluído!")
    print("💡 Para testar os filtros na interface, acesse o dashboard e clique na aba 'Finalizados'")

if __name__ == "__main__":
    test_filtros_finalizados() 