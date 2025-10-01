#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Servidor simples para testar visualizacao RNC."""

from flask import Flask, render_template, session, redirect
import sqlite3

app = Flask(__name__)
app.secret_key = 'test_secret'

@app.route('/')
def index():
    session['user_id'] = 1  # Mock user
    return redirect('/rnc/1')

@app.route('/rnc/<int:rnc_id>')
def view_rnc(rnc_id):
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rncs WHERE id = ?', (rnc_id,))
        rnc_data = cursor.fetchone()
        
        if not rnc_data:
            return "<h1>RNC nao encontrado</h1><p>ID buscado: {}</p>".format(rnc_id)
        
        # Obter nomes das colunas
        cursor.execute('PRAGMA table_info(rncs)')
        columns = [row[1] for row in cursor.fetchall()]
        
        # Criar dicionario
        rnc_dict = dict(zip(columns, rnc_data))
        
        print(f"DEBUG: RNC encontrado: {rnc_dict.get('rnc_number')}")
        print(f"DEBUG: Total de campos: {len(rnc_dict)}")
        
        conn.close()
        
        # Criar resposta sem CSP restritivo usando template simplificado
        from flask import make_response
        response = make_response(render_template('view_rnc_simple.html', rnc=rnc_dict))
        response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: https:; style-src 'self' 'unsafe-inline' https:; font-src 'self' data: https:; script-src 'self' 'unsafe-inline' 'unsafe-eval';"
        return response
    except Exception as e:
        import traceback
        return f"<h1>Erro:</h1><pre>{e}\n\n{traceback.format_exc()}</pre>"

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)