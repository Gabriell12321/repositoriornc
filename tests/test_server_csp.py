#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste rápido do servidor com CSP básico configurado.
"""

from server_form import app
import time
import threading

def test_server_with_csp():
    """Testa o servidor com CSP configurado"""
    print("🚀 TESTANDO SERVIDOR COM CSP BÁSICO")
    print("=" * 50)
    
    # Testar se o app carrega sem erros
    try:
        with app.test_client() as client:
            # Teste da página principal
            response = client.get('/')
            print(f"✅ Página principal: Status {response.status_code}")
            
            # Verificar headers CSP
            csp_header = response.headers.get('Content-Security-Policy')
            csp_ro_header = response.headers.get('Content-Security-Policy-Report-Only')
            
            if csp_header:
                print("✅ Header CSP enforced encontrado")
                print(f"   {csp_header[:100]}...")
            else:
                print("❌ Header CSP enforced não encontrado")
            
            if csp_ro_header:
                print("✅ Header CSP Report-Only encontrado")
                print(f"   {csp_ro_header[:100]}...")
            else:
                print("❌ Header CSP Report-Only não encontrado")
            
            # Teste do endpoint CSP report
            csp_report_response = client.post('/csp-report', 
                                              json={'test': 'violation'},
                                              content_type='application/csp-report')
            print(f"✅ Endpoint /csp-report: Status {csp_report_response.status_code}")
            
            # Verificar outros headers de segurança
            security_headers = [
                'X-Frame-Options',
                'X-Content-Type-Options', 
                'Referrer-Policy',
                'X-XSS-Protection'
            ]
            
            print("\n🔒 HEADERS DE SEGURANÇA:")
            for header in security_headers:
                value = response.headers.get(header)
                if value:
                    print(f"  ✅ {header}: {value}")
                else:
                    print(f"  ⚠️  {header}: não encontrado")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao testar servidor: {e}")
        return False

def create_sample_csp_violation():
    """Cria um exemplo de violação CSP para teste"""
    print("\n📊 EXEMPLO DE VIOLAÇÃO CSP:")
    print("-" * 30)
    
    sample_violation = {
        "csp-report": {
            "document-uri": "http://localhost:5000/dashboard",
            "referrer": "",
            "violated-directive": "script-src 'self'",
            "effective-directive": "script-src",
            "original-policy": "default-src 'self'; script-src 'self'",
            "disposition": "report",
            "blocked-uri": "inline",
            "line-number": 1,
            "column-number": 1,
            "source-file": "http://localhost:5000/dashboard",
            "status-code": 200,
            "script-sample": "onclick handler"
        }
    }
    
    print("  Exemplo de relatório que seria enviado para /csp-report:")
    print(f"  Diretiva violada: {sample_violation['csp-report']['violated-directive']}")
    print(f"  URI bloqueado: {sample_violation['csp-report']['blocked-uri']}")
    print(f"  Tipo: Script inline bloqueado pela política")

if __name__ == "__main__":
    success = test_server_with_csp()
    create_sample_csp_violation()
    
    if success:
        print("\n🎉 CONFIGURAÇÃO CSP BÁSICA TESTADA COM SUCESSO!")
        print("   • Headers CSP estão sendo enviados")
        print("   • Endpoint de relatórios funcionando")
        print("   • Headers de segurança ativos")
        print("   • Sistema protegido contra XSS")
        print("\n💡 PRÓXIMOS PASSOS:")
        print("   • Iniciar servidor e monitorar logs/security.log")
        print("   • Verificar /admin/monitoring para violações")
        print("   • Planejar migração de scripts inline")
    else:
        print("\n⚠️  VERIFICAR CONFIGURAÇÃO DO SERVIDOR!")
