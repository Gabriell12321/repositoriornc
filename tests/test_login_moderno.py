#!/usr/bin/env python3
"""
Script para testar a nova página de login moderna
"""

import requests
import time
from datetime import datetime

def test_login_page():
    """Testa a página de login moderna"""
    print("🎨 Testando Página de Login Moderna...")
    
    # URL base do servidor
    base_url = "http://localhost:5000"
    
    # 1. Testar acesso à página de login
    print("\n1️⃣ Testando acesso à página de login...")
    
    try:
        response = requests.get(f"{base_url}/")
        
        if response.status_code == 200:
            print("✅ Página de login acessível")
            
            # Verificar elementos modernos
            html_content = response.text
            
            # Verificar fontes modernas
            if "Inter" in html_content or "font-awesome" in html_content:
                print("✅ Fontes modernas carregadas")
            else:
                print("⚠️ Fontes modernas não encontradas")
            
            # Verificar animações
            if "cubic-bezier" in html_content or "backdrop-filter" in html_content:
                print("✅ Animações modernas implementadas")
            else:
                print("⚠️ Animações modernas não encontradas")
            
            # Verificar ícones Font Awesome
            if "fas fa-envelope" in html_content and "fas fa-lock" in html_content:
                print("✅ Ícones Font Awesome implementados")
            else:
                print("⚠️ Ícones Font Awesome não encontrados")
            
            # Verificar contas de demonstração
            if "admin@ippel.com" in html_content and "user@ippel.com" in html_content:
                print("✅ Contas de demonstração configuradas")
            else:
                print("⚠️ Contas de demonstração não encontradas")
                
        else:
            print(f"❌ Erro ao acessar página: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar página: {e}")
        return False
    
    # 2. Testar funcionalidade de login
    print("\n2️⃣ Testando funcionalidade de login...")
    
    test_accounts = [
        {"email": "admin@ippel.com", "password": "admin123", "role": "Administrador"},
        {"email": "user@ippel.com", "password": "user123", "role": "Usuário"},
        {"email": "engenheiro@ippel.com", "password": "eng123", "role": "Engenheiro"}
    ]
    
    for account in test_accounts:
        print(f"\n   🔐 Testando login: {account['role']}")
        
        try:
            session = requests.Session()
            response = session.post(f"{base_url}/api/login", json={
                "email": account["email"],
                "password": account["password"]
            })
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data or "user_id" in data:
                    print(f"   ✅ Login {account['role']} funcionando")
                    
                    # Testar acesso ao dashboard
                    dashboard_response = session.get(f"{base_url}/dashboard")
                    if dashboard_response.status_code == 200:
                        print(f"   ✅ Dashboard acessível para {account['role']}")
                    else:
                        print(f"   ⚠️ Dashboard não acessível para {account['role']}")
                else:
                    print(f"   ❌ Login {account['role']} falhou")
            else:
                print(f"   ❌ Erro no login {account['role']}: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro ao testar login {account['role']}: {e}")
    
    # 3. Testar responsividade
    print("\n3️⃣ Testando responsividade...")
    
    try:
        # Simular diferentes tamanhos de tela
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        }
        
        response = requests.get(f"{base_url}/", headers=headers)
        
        if response.status_code == 200:
            html_content = response.text
            
            # Verificar CSS responsivo
            if "@media" in html_content and "max-width" in html_content:
                print("✅ CSS responsivo implementado")
            else:
                print("⚠️ CSS responsivo não encontrado")
            
            # Verificar viewport meta tag
            if "viewport" in html_content:
                print("✅ Meta viewport configurado")
            else:
                print("⚠️ Meta viewport não encontrado")
                
        else:
            print(f"❌ Erro ao testar responsividade: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar responsividade: {e}")
    
    # 4. Testar performance
    print("\n4️⃣ Testando performance...")
    
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/")
        load_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Página carregada em {load_time:.2f} segundos")
            
            if load_time < 2.0:
                print("✅ Performance excelente")
            elif load_time < 3.0:
                print("✅ Performance boa")
            else:
                print("⚠️ Performance pode ser melhorada")
        else:
            print(f"❌ Erro ao testar performance: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar performance: {e}")
    
    print("\n🎯 Teste da página de login concluído!")
    return True

def test_modern_features():
    """Testa recursos modernos específicos"""
    print("\n🔍 Testando recursos modernos...")
    
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(f"{base_url}/")
        html_content = response.text
        
        modern_features = [
            ("Gradientes CSS", "linear-gradient"),
            ("Backdrop Filter", "backdrop-filter"),
            ("Animações CSS", "cubic-bezier"),
            ("Font Awesome", "font-awesome"),
            ("Google Fonts", "fonts.googleapis.com"),
            ("Partículas", "particle"),
            ("Glassmorphism", "rgba(255, 255, 255, 0.95)"),
            ("Sombras modernas", "box-shadow"),
            ("Border radius", "border-radius: 30px"),
            ("Transições suaves", "transition")
        ]
        
        for feature_name, feature_check in modern_features:
            if feature_check in html_content:
                print(f"   ✅ {feature_name}")
            else:
                print(f"   ❌ {feature_name}")
                
    except Exception as e:
        print(f"❌ Erro ao testar recursos modernos: {e}")

def test_user_experience():
    """Testa a experiência do usuário"""
    print("\n👤 Testando experiência do usuário...")
    
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(f"{base_url}/")
        html_content = response.text
        
        ux_features = [
            ("Placeholders nos campos", "placeholder="),
            ("Ícones nos campos", "input-icon"),
            ("Animações de hover", "hover"),
            ("Feedback visual", "focus"),
            ("Loading states", "loading"),
            ("Mensagens de erro", "message error"),
            ("Mensagens de sucesso", "message success"),
            ("Contas de demonstração", "demo-account"),
            ("Botões de copiar", "demo-copy"),
            ("Foco automático", "focus()")
        ]
        
        for feature_name, feature_check in ux_features:
            if feature_check in html_content:
                print(f"   ✅ {feature_name}")
            else:
                print(f"   ❌ {feature_name}")
                
    except Exception as e:
        print(f"❌ Erro ao testar UX: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando testes da página de login moderna")
    print("=" * 60)
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        print("✅ Servidor está rodando")
    except:
        print("❌ Servidor não está rodando. Inicie o servidor primeiro!")
        exit(1)
    
    # Executar testes
    test_login_page()
    test_modern_features()
    test_user_experience()
    
    print("\n🎉 Testes concluídos!")
    print("\n💡 Para testar a página de login no navegador:")
    print("   1. Acesse: http://localhost:5000")
    print("   2. Teste as contas de demonstração")
    print("   3. Verifique as animações e efeitos")
    print("   4. Teste em diferentes tamanhos de tela")
    print("   5. Verifique a responsividade") 