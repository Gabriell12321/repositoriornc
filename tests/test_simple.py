#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples para verificar o sistema IPPEL
"""

import requests
import json
import sqlite3

def test_basic():
    print("Testando sistema IPPEL...")
    
    # Teste 1: Conexao com servidor
    try:
        response = requests.get("http://192.168.3.11:5001/", timeout=5)
        print(f"Servidor respondendo: {response.status_code}")
    except Exception as e:
        print(f"Erro de conexao: {e}")
        return False
    
    # Teste 2: Banco de dados
    try:
        conn = sqlite3.connect('ippel_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM rncs")
        count = cursor.fetchone()[0]
        print(f"Total de RNCs no banco: {count}")
        conn.close()
    except Exception as e:
        print(f"Erro no banco: {e}")
        return False
    
    # Teste 3: API de RNCs
    try:
        response = requests.get("http://192.168.3.11:5001/api/rnc/list", timeout=5)
        print(f"API RNC status: {response.status_code}")
        if response.status_code == 401:
            print("API protegida (correto)")
        else:
            print(f"Resposta: {response.text[:200]}")
    except Exception as e:
        print(f"Erro na API: {e}")
    
    return True

if __name__ == "__main__":
    test_basic()