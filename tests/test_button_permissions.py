import requests
import json

def test_button_functionality():
    """Testa se o botão e a funcionalidade estão funcionando"""
    base_url = "http://127.0.0.1:5001"
    
    print("🧪 TESTE DO BOTÃO 'GERENCIAR PERMISSÕES CRIAÇÃO RNC'")
    print("="*60)
    
    # 1. Testar se a página principal carrega
    print("1️⃣ Testando dashboard principal...")
    try:
        response = requests.get(f"{base_url}/dashboard", timeout=5)
        if response.status_code == 200:
            print("   ✅ Dashboard carregou com sucesso")
            
            # Verificar se o botão está no HTML
            html_content = response.text
            if 'manageFieldLocksBtn' in html_content:
                print("   ✅ Botão encontrado no HTML")
            else:
                print("   ❌ Botão NÃO encontrado no HTML")
                
            if 'Gerenciar Permissões Criação RNC' in html_content:
                print("   ✅ Texto do botão encontrado")
            else:
                print("   ❌ Texto do botão NÃO encontrado")
                
            if 'display: flex !important' in html_content:
                print("   ✅ Botão está visível (display: flex !important)")
            else:
                print("   ⚠️ Botão pode estar oculto")
                
        else:
            print(f"   ❌ Dashboard falhou: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro ao acessar dashboard: {e}")
    
    # 2. Testar se a página de permissões carrega
    print("\n2️⃣ Testando página de permissões...")
    try:
        response = requests.get(f"{base_url}/admin/field-locks/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Página de permissões carregou com sucesso")
        elif response.status_code == 403:
            print("   ⚠️ Acesso negado (precisa fazer login como admin)")
        else:
            print(f"   ❌ Página de permissões falhou: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro ao acessar permissões: {e}")
    
    # 3. Testar APIs
    print("\n3️⃣ Testando APIs...")
    
    # API de campos
    try:
        response = requests.get(f"{base_url}/admin/field-locks/api/fields", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                fields_count = len(data.get('fields', {}))
                print(f"   ✅ API de campos funcionando: {fields_count} campos disponíveis")
            else:
                print("   ❌ API de campos retornou erro")
        elif response.status_code == 403:
            print("   ⚠️ API de campos: acesso negado (precisa login)")
        else:
            print(f"   ❌ API de campos falhou: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro na API de campos: {e}")
    
    # API de grupos
    try:
        response = requests.get(f"{base_url}/admin/field-locks/api/groups", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                groups_count = len(data.get('groups', []))
                print(f"   ✅ API de grupos funcionando: {groups_count} grupos disponíveis")
            else:
                print("   ❌ API de grupos retornou erro")
        elif response.status_code == 403:
            print("   ⚠️ API de grupos: acesso negado (precisa login)")
        else:
            print(f"   ❌ API de grupos falhou: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro na API de grupos: {e}")
    
    # 4. Instruções de uso
    print("\n4️⃣ Instruções de uso:")
    print("   📋 1. Acesse: http://127.0.0.1:5001/")
    print("   🔑 2. Faça login como admin@ippel.com.br / admin123")
    print("   🎯 3. No dashboard, procure o botão '🔐 Gerenciar Permissões Criação RNC'")
    print("   ⚡ 4. O botão deve estar na seção 'Ações Rápidas'")
    print("   🔗 5. Clique para acessar: http://127.0.0.1:5001/admin/field-locks/")
    
    # 5. Status visual do botão
    print("\n5️⃣ Características do botão:")
    print("   🎨 Cor: Gradiente vermelho (#e74c3c → #c0392b)")
    print("   📝 Texto: '🔐 Gerenciar Permissões Criação RNC'")
    print("   📍 Localização: Após '🔐 Gerenciar Permissões'")
    print("   👀 Visibilidade: Forçada (display: flex !important)")
    print("   🎯 ID: manageFieldLocksBtn")
    
    print("\n✅ Teste concluído!")
    print("🌐 Se o botão não aparecer, verifique:")
    print("   • Cache do navegador (Ctrl+F5)")
    print("   • Permissões de admin")
    print("   • Console do navegador (F12)")

if __name__ == "__main__":
    test_button_functionality()