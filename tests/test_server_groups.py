#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import requests
import time

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_server():
    """Testar se o servidor está rodando e a página de grupos funciona"""
    
    print("🔍 Testando servidor...")
    
    # Testar se o servidor está rodando
    try:
        response = requests.get('http://172.26.0.252:5001/', timeout=5)
        print(f"✅ Servidor está rodando (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está rodando na porta 5001")
        print("💡 Execute: python server_form.py")
        return False
    except Exception as e:
        print(f"❌ Erro ao conectar com servidor: {e}")
        return False
    
    # Testar página de login
    try:
        response = requests.get('http://172.26.0.252:5001/', timeout=5)
        if response.status_code == 200:
            print("✅ Página de login carregada")
        else:
            print(f"⚠️ Página de login retornou status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar página de login: {e}")
    
    # Testar página de grupos (deve redirecionar para login se não autenticado)
    try:
        response = requests.get('http://172.26.0.252:5001/admin/groups', timeout=5, allow_redirects=False)
        if response.status_code == 302:
            print("✅ Página de grupos redirecionando corretamente (não autenticado)")
        elif response.status_code == 200:
            print("✅ Página de grupos carregada (usuário autenticado)")
        else:
            print(f"⚠️ Página de grupos retornou status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao acessar página de grupos: {e}")
    
    print("\n📋 Resumo:")
    print("1. Se o servidor não está rodando, execute: python server_form.py")
    print("2. Se está rodando mas a página fica branca, pode ser problema de autenticação")
    print("3. Faça login primeiro e depois acesse /admin/groups")
    
    return True

if __name__ == "__main__":
    test_server() 