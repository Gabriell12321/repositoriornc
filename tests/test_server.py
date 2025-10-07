#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("=== TESTE DE SERVIDOR IPPEL ===")

try:
    import sys
    print(f"✅ Python version: {sys.version}")
except Exception as e:
    print(f"❌ Erro no sys: {e}")

try:
    import sqlite3
    print("✅ SQLite3 disponível")
except Exception as e:
    print(f"❌ SQLite3 erro: {e}")

try:
    import flask
    print(f"✅ Flask version: {flask.__version__}")
except Exception as e:
    print(f"❌ Flask não encontrado: {e}")

try:
    import flask_login
    print(f"✅ Flask-Login disponível")
except Exception as e:
    print(f"❌ Flask-Login não encontrado: {e}")

print("\n=== TENTANDO INICIAR SERVIDOR SIMPLES ===")

try:
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return '''
        <h1>🚀 SERVIDOR IPPEL FUNCIONANDO!</h1>
        <p>✅ Flask está funcionando corretamente</p>
        <p>📧 Sistema RNC IPPEL - Porta 5001</p>
        <p><a href="/status">Verificar Status</a></p>
        '''
    
    @app.route('/status')
    def status():
        return {
            'status': 'online',
            'message': 'Servidor IPPEL funcionando',
            'python_version': sys.version,
            'flask_version': flask.__version__
        }
    
    print("🚀 Iniciando servidor simples na porta 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)

except Exception as e:
    print(f"❌ Erro ao iniciar servidor: {e}")
    import traceback
    traceback.print_exc()
