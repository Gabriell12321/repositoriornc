#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
⚡ Teste de Integração das Melhorias de Segurança
Arquivo para testar e validar o sistema de segurança
"""

import os
import sys

def test_security_imports():
    """Testar importações dos módulos de segurança"""
    try:
        from security_enhancements import SecurityManager, SECURITY_CONFIG
        from two_factor_auth import TwoFactorAuth
        from security_routes import init_security_routes
        
        print("✅ Todos os módulos de segurança importados com sucesso")
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        return False

def test_dependencies():
    """Testar dependências necessárias"""
    packages = ['pyotp', 'qrcode', 'PIL']
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - Não encontrado")
            return False
    
    return True

def create_security_tables():
    """Criar tabelas de segurança no banco"""
    try:
        import sqlite3
        from security_enhancements import SecurityManager
        from two_factor_auth import TwoFactorAuth
        
        # Testar criação das tabelas
        security_manager = SecurityManager(None, 'ippel_system.db')
        tfa_system = TwoFactorAuth('ippel_system.db')
        
        print("✅ Tabelas de segurança criadas/verificadas")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

def show_integration_guide():
    """Mostrar guia de integração"""
    print("\n" + "="*60)
    print("🔐 GUIA DE INTEGRAÇÃO DE SEGURANÇA")
    print("="*60)
    
    print("\n1. MODIFICAÇÕES NO server_form.py:")
    print("   - Adicionar importações de segurança após as existentes")
    print("   - Inicializar SecurityManager após criar app Flask")
    print("   - Registrar rotas de segurança")
    
    print("\n2. CÓDIGO PARA ADICIONAR:")
    print("""
# Após as importações existentes, adicionar:
try:
    from security_enhancements import SecurityManager, add_security_headers
    from two_factor_auth import TwoFactorAuth  
    from security_routes import init_security_routes
    SECURITY_ENABLED = True
    print("🔐 Sistema de segurança carregado")
except ImportError as e:
    SECURITY_ENABLED = False
    print(f"⚠️ Segurança não disponível: {e}")

# Após criar app = Flask(__name__), adicionar:
if SECURITY_ENABLED:
    security_manager = SecurityManager(app)
    tfa_system = TwoFactorAuth()
    init_security_routes(app)
    
    @app.before_request
    def security_middleware():
        from flask import g
        g.security_manager = security_manager
    
    @app.after_request
    def add_security_headers_middleware(response):
        return add_security_headers(response)
""")
    
    print("\n3. NOVAS ROTAS DISPONÍVEIS:")
    print("   - /security/login          - Login com verificações avançadas")
    print("   - /security/setup-2fa      - Configurar autenticação 2FA") 
    print("   - /security/verify-2fa     - Verificar código 2FA")
    print("   - /security/change-password - Alterar senha com validações")
    print("   - /security/security-audit - Relatório de auditoria")
    print("   - /security-dashboard      - Dashboard de segurança")
    
    print("\n4. RECURSOS DE SEGURANÇA:")
    print("   ✅ Autenticação de dois fatores (2FA)")
    print("   ✅ Validação de força de senha")
    print("   ✅ Sistema de auditoria completo")
    print("   ✅ Proteção contra força bruta")
    print("   ✅ Blacklist automática de IPs")
    print("   ✅ Headers de segurança HTTP")
    print("   ✅ Proteção CSRF")
    print("   ✅ Gestão de sessões seguras")
    print("   ✅ Logs detalhados de segurança")
    
    print("\n5. CONFIGURAÇÕES DE SEGURANÇA:")
    print("   - Máximo de tentativas de login: 5")
    print("   - Tempo de bloqueio: 30 minutos") 
    print("   - Timeout de sessão: 8 horas")
    print("   - Senha mínima: 8 caracteres")
    print("   - Códigos de backup 2FA: 10")
    
    print("\n6. DASHBOARD DE SEGURANÇA:")
    print("   - Acesse: http://SEU_IP:5001/security-dashboard")
    print("   - Configure 2FA para usuários")
    print("   - Monitore atividades suspeitas")
    print("   - Gerencie sessões ativas")

if __name__ == "__main__":
    print("🔐 TESTE DO SISTEMA DE SEGURANÇA IPPEL")
    print("="*50)
    
    # Teste 1: Dependências
    print("\n📦 Testando dependências...")
    if not test_dependencies():
        print("❌ Instale as dependências primeiro")
        sys.exit(1)
    
    # Teste 2: Importações
    print("\n📥 Testando importações...")
    if not test_security_imports():
        print("❌ Erro nas importações")
        sys.exit(1)
    
    # Teste 3: Banco de dados
    print("\n🗄️ Testando banco de dados...")
    if not create_security_tables():
        print("❌ Erro no banco")
        sys.exit(1)
    
    print("\n✅ TODOS OS TESTES PASSARAM!")
    show_integration_guide()
    
    print(f"\n🎉 Sistema de segurança pronto para integração!")
    print("📄 Templates criados:")
    print("   - templates/security_dashboard.html")
    print("📁 Arquivos de segurança:")
    print("   - security_enhancements.py")
    print("   - two_factor_auth.py") 
    print("   - security_routes.py")
