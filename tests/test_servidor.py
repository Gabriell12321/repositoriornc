#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Teste simples do servidor."""

from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/test_data')
def test_data():
    conn = sqlite3.connect('ippel_system.db')
    cursor = conn.cursor()
    
    # Buscar alguns RNCs com os novos campos
    rncs = cursor.execute("""
        SELECT rnc_number, area_responsavel, setor, responsavel
        FROM rncs 
        WHERE area_responsavel IS NOT NULL AND area_responsavel != ""
        LIMIT 5
    """).fetchall()
    
    result = []
    for rnc in rncs:
        result.append({
            'rnc_number': rnc[0],
            'area_responsavel': rnc[1], 
            'setor': rnc[2],
            'responsavel': rnc[3]
        })
    
    conn.close()
    return jsonify(result)

if __name__ == '__main__':
    print("Testando dados atualizados...")
    app.run(debug=True, host='127.0.0.1', port=5001)