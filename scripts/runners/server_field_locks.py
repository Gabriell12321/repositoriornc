#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask_cors import CORS
from routes.field_locks import field_locks_bp
import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)

# Registrar blueprint
app.register_blueprint(field_locks_bp)

@app.route('/')
def index():
    return '''
    <h1>Servidor Field Locks API</h1>
    <p><a href="/admin/field-locks/">Interface de Permissões</a></p>
    <p><a href="/admin/field-locks/api/groups">API de Grupos</a></p>
    '''

if __name__ == '__main__':
    print("🔐 Iniciando servidor Field Locks...")
    print("📄 Acesse: http://localhost:5001")
    print("🔧 Interface: http://localhost:5001/admin/field-locks/")
    print()
    
    app.run(host='0.0.0.0', port=5001, debug=True)