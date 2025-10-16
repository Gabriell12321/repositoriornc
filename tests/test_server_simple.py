#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples do servidor Flask
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Servidor funcionando!'

@app.route('/test')
def test():
    return 'Rota de teste funcionando!'

if __name__ == '__main__':
    print("🚀 Iniciando servidor de teste...")
    print("📄 Acesse: http://localhost:5000")
    print("🧪 Teste: http://localhost:5000/test")
    print()
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        import traceback
        traceback.print_exc()
