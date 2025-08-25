#!/usr/bin/env python3
"""Script para testar e diagnosticar problemas com HTTPS"""
import os
import sys

print("🔍 Testando configuração HTTPS...")
print("=" * 50)

# Testar imports necessários
try:
    from flask import Flask
    print("✅ Flask instalado")
except ImportError as e:
    print(f"❌ Flask não instalado: {e}")
    sys.exit(1)

try:
    from flask_socketio import SocketIO
    print("✅ Flask-SocketIO instalado")
except ImportError as e:
    print(f"❌ Flask-SocketIO não instalado: {e}")
    sys.exit(1)

try:
    import ssl
    print("✅ SSL disponível")
except ImportError as e:
    print(f"❌ SSL não disponível: {e}")
    sys.exit(1)

try:
    import OpenSSL
    print(f"✅ pyOpenSSL instalado (versão {OpenSSL.__version__})")
except ImportError as e:
    print(f"❌ pyOpenSSL não instalado: {e}")
    print("   Execute: pip install pyOpenSSL")
    sys.exit(1)

# Testar criação de certificado adhoc
print("\n🔒 Testando certificado adhoc...")
try:
    from werkzeug.serving import make_ssl_devcert
    cert, key = make_ssl_devcert('cert', host='localhost')
    print(f"✅ Certificado criado: {cert}")
    print(f"✅ Chave criada: {key}")
    
    # Limpar arquivos temporários
    import os
    if os.path.exists(cert):
        os.remove(cert)
    if os.path.exists(key):
        os.remove(key)
except Exception as e:
    print(f"❌ Erro ao criar certificado: {e}")
    import traceback
    traceback.print_exc()

# Testar servidor mínimo com HTTPS
print("\n🚀 Iniciando servidor de teste HTTPS...")
try:
    app = Flask(__name__)
    
    @app.route('/')
    def test():
        return 'HTTPS funcionando!'
    
    @app.route('/api/test')
    def api_test():
        return {'status': 'ok', 'https': True}
    
    print("📋 Acesse: https://localhost:5002")
    print("   (aceite o aviso de certificado autoassinado)")
    print("\nPressione Ctrl+C para parar...")
    
    # Iniciar com ssl_context='adhoc'
    app.run(host='0.0.0.0', port=5002, ssl_context='adhoc', debug=False)
    
except KeyboardInterrupt:
    print("\n👋 Teste encerrado")
except Exception as e:
    print(f"❌ Erro ao iniciar servidor: {e}")
    import traceback
    traceback.print_exc()
